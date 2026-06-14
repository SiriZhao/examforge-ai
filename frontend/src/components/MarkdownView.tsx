import type { ReactNode } from "react";

type MarkdownViewProps = {
  markdown: string;
};

export function MarkdownView({ markdown }: MarkdownViewProps) {
  return <div className="markdown-view">{renderMarkdown(markdown)}</div>;
}

function renderMarkdown(markdown: string) {
  const lines = markdown.split("\n");
  const nodes: ReactNode[] = [];
  let listItems: string[] = [];
  let tableRows: string[][] = [];

  function flushList() {
    if (listItems.length > 0) {
      nodes.push(
        <ul key={`list-${nodes.length}`}>
          {listItems.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>,
      );
      listItems = [];
    }
  }

  function flushTable() {
    if (tableRows.length > 0) {
      const [head, ...body] = tableRows;
      nodes.push(
        <div className="markdown-table-wrap" key={`table-${nodes.length}`}>
          <table>
            <thead>
              <tr>
                {head.map((cell, index) => (
                  <th key={index}>{cell}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {body.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {row.map((cell, cellIndex) => (
                    <td key={cellIndex}>{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>,
      );
      tableRows = [];
    }
  }

  lines.forEach((line, index) => {
    const trimmed = line.trim();
    if (!trimmed) {
      flushList();
      flushTable();
      return;
    }
    if (trimmed.startsWith("|") && trimmed.endsWith("|")) {
      const cells = trimmed
        .slice(1, -1)
        .split("|")
        .map((cell) => cell.trim());
      if (!cells.every((cell) => /^:?-+:?$/.test(cell))) {
        tableRows.push(cells);
      }
      return;
    }
    flushTable();
    if (trimmed.startsWith("- ")) {
      listItems.push(trimmed.slice(2));
      return;
    }
    flushList();
    if (trimmed.startsWith("### ")) {
      nodes.push(<h3 key={index}>{trimmed.slice(4)}</h3>);
    } else if (trimmed.startsWith("## ")) {
      nodes.push(<h2 key={index}>{trimmed.slice(3)}</h2>);
    } else if (trimmed.startsWith("# ")) {
      nodes.push(<h1 key={index}>{trimmed.slice(2)}</h1>);
    } else {
      nodes.push(<p key={index}>{trimmed.replace(/`/g, "")}</p>);
    }
  });

  flushList();
  flushTable();
  return nodes;
}
