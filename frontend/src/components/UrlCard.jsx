import { getUrlStats } from "../api/client";
import { usePolling } from "../hooks/usePolling";
import { CopyButton } from "./CopyButton";

export function UrlCard({ link, isSelected, onSelect, onRemove }) {
  const { data: stats } = usePolling(() => getUrlStats(link.shortCode), {
    intervalMs: 5000,
  });

  return (
    <div className={`url-card ${isSelected ? "url-card--selected" : ""}`} onClick={() => onSelect(link.shortCode)}>
      <div className="url-card__main">
        <div className="url-card__short">{link.shortUrl}</div>
        <div className="url-card__original" title={link.originalUrl}>
          {link.originalUrl}
        </div>
      </div>
      <div className="url-card__clicks">
        <span className="url-card__click-count">{stats ? stats.total_clicks : "…"}</span>
        <span className="url-card__click-label">clicks</span>
      </div>
      <div className="url-card__actions">
        <CopyButton text={link.shortUrl} />
        <button
          type="button"
          className="remove-button"
          onClick={(e) => {
            e.stopPropagation();
            onRemove(link.shortCode);
          }}
        >
          Remove
        </button>
      </div>
    </div>
  );
}
