function parseBlocks(content) {
  const lines = content.split(/\r?\n/);
  const blocks = [];
  let paragraph = [];
  let list = [];

  function flushParagraph() {
    if (paragraph.length) {
      blocks.push({ type: "paragraph", content: paragraph.join(" ").trim() });
      paragraph = [];
    }
  }

  function flushList() {
    if (list.length) {
      blocks.push({ type: "list", items: list });
      list = [];
    }
  }

  for (const rawLine of lines) {
    const line = rawLine.trim();

    if (!line) {
      flushParagraph();
      flushList();
      continue;
    }

    if (/^#{1,3}\s+/.test(line)) {
      flushParagraph();
      flushList();
      blocks.push({ type: "heading", content: line.replace(/^#{1,3}\s+/, "") });
      continue;
    }

    if (/^(\-|\*|\u2022)\s+/.test(line)) {
      flushParagraph();
      list.push(line.replace(/^(\-|\*|\u2022)\s+/, ""));
      continue;
    }

    if (/^\d+\.\s+/.test(line)) {
      flushParagraph();
      list.push(line.replace(/^\d+\.\s+/, ""));
      continue;
    }

    flushList();
    paragraph.push(line);
  }

  flushParagraph();
  flushList();
  return blocks;
}

export default function RichTextMessage({ content }) {
  const blocks = parseBlocks(content);

  return (
    <div className="rich-text">
      {blocks.map((block, index) => {
        if (block.type === "heading") {
          return <h3 key={index}>{block.content}</h3>;
        }

        if (block.type === "list") {
          return (
            <ul key={index}>
              {block.items.map((item, itemIndex) => (
                <li key={itemIndex}>{item}</li>
              ))}
            </ul>
          );
        }

        return <p key={index}>{block.content}</p>;
      })}
    </div>
  );
}
