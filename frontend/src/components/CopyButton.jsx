import { useState } from "react";

export function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <button type="button" className="copy-button" onClick={handleCopy}>
      {copied ? "Copied!" : "Copy"}
    </button>
  );
}
