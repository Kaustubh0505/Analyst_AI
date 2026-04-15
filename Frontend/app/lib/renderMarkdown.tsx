/**
 * Converts a subset of Markdown in LLM responses into React elements.
 * Currently supports:
 *   - **bold** → <strong>bold</strong>
 *   - `code` → <code>code</code>
 */
export function renderMarkdown(text: string): React.ReactNode[] {
  // Split on **...** and `...` patterns
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);

  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code
          key={i}
          style={{
            background: "rgba(99,102,241,0.08)",
            color: "var(--accent-primary)",
            padding: "1px 6px",
            borderRadius: 4,
            fontSize: "0.92em",
            fontFamily: "monospace",
          }}
        >
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });
}
