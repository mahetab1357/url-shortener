import { useState } from "react";
import { Link } from "react-router-dom";
import { AlertCircle, ArrowRight, Calendar, Link2, Sparkles, Tag } from "lucide-react";
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
      <div className="page-header">
        <span className="page-header__eyebrow">
          <Sparkles size={13} />
          Fast, cached, trackable
        </span>
        <h1>Shorten a URL</h1>
        <p>Paste a long link below and get a short, shareable one in seconds.</p>
      </div>

      <form onSubmit={handleSubmit} className="shorten-form">
        <label htmlFor="url">Long URL</label>
        <div className="input-wrap">
          <Link2 size={16} />
          <input
            id="url"
            type="url"
            placeholder="https://example.com/some/very/long/path"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
          />
        </div>

        <label htmlFor="customAlias">Custom alias (optional)</label>
        <div className="input-wrap">
          <Tag size={16} />
          <input
            id="customAlias"
            type="text"
            placeholder="my-cool-link"
            value={customAlias}
            onChange={(e) => setCustomAlias(e.target.value)}
          />
        </div>

        <label htmlFor="expiresAt">Expires at (optional)</label>
        <div className="input-wrap">
          <Calendar size={16} />
          <input
            id="expiresAt"
            type="datetime-local"
            value={expiresAt}
            onChange={(e) => setExpiresAt(e.target.value)}
          />
        </div>

        <button type="submit" disabled={submitting}>
          {submitting ? (
            <>
              <span className="spinner" />
              Shortening…
            </>
          ) : (
            <>
              Shorten link
              <ArrowRight size={17} />
            </>
          )}
        </button>
      </form>

      {error && (
        <p className="error-message">
          <AlertCircle size={16} />
          {error}
        </p>
      )}

      {result && (
        <div className="result-card">
          <div className="result-card__main">
            <Link2 size={18} />
            <span className="result-card__url">{result.short_url}</span>
          </div>
          <CopyButton text={result.short_url} />
        </div>
      )}

      <p className="page-footer">
        <Link to="/dashboard">View your dashboard →</Link>
      </p>
    </div>
  );
}
