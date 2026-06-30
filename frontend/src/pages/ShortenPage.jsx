import { useState } from "react";
import { Link } from "react-router-dom";
import { shortenUrl, ApiError } from "../api/client";
import { useMyLinks } from "../hooks/useMyLinks";
import { CopyButton } from "../components/CopyButton";

export function ShortenPage() {
  const [url, setUrl] = useState("");
  const [customAlias, setCustomAlias] = useState("");
  const [expiresAt, setExpiresAt] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const { addLink } = useMyLinks();

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const expiresAtIso = expiresAt ? new Date(expiresAt).toISOString() : null;
      const response = await shortenUrl({ url, customAlias, expiresAt: expiresAtIso });
      setResult(response);
      addLink({
        shortCode: response.short_code,
        shortUrl: response.short_url,
        originalUrl: response.original_url,
        createdAt: response.created_at,
      });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page">
      <h1>Shorten a URL</h1>
      <form onSubmit={handleSubmit} className="shorten-form">
        <label htmlFor="url">Long URL</label>
        <input
          id="url"
          type="url"
          placeholder="https://example.com/some/very/long/path"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
        />

        <label htmlFor="customAlias">Custom alias (optional)</label>
        <input
          id="customAlias"
          type="text"
          placeholder="my-cool-link"
          value={customAlias}
          onChange={(e) => setCustomAlias(e.target.value)}
        />

        <label htmlFor="expiresAt">Expires at (optional)</label>
        <input
          id="expiresAt"
          type="datetime-local"
          value={expiresAt}
          onChange={(e) => setExpiresAt(e.target.value)}
        />

        <button type="submit" disabled={submitting}>
          {submitting ? "Shortening…" : "Shorten"}
        </button>
      </form>

      {error && <p className="error-message">{error}</p>}

      {result && (
        <div className="result-card">
          <span className="result-card__url">{result.short_url}</span>
          <CopyButton text={result.short_url} />
        </div>
      )}

      <p className="page-footer">
        <Link to="/dashboard">View your dashboard →</Link>
      </p>
    </div>
  );
}
