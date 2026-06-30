import { useEffect } from "react";
import { Link2, X } from "lucide-react";
import { getUrlStats } from "../api/client";
import { usePolling } from "../hooks/usePolling";
import { CopyButton } from "./CopyButton";

export function UrlCard({ link, isSelected, onSelect, onRemove, onStatsUpdate }) {
  const { data: stats } = usePolling(() => getUrlStats(link.shortCode), {
    intervalMs: 5000,
  });

  useEffect(() => {
    if (stats && onStatsUpdate) {
      onStatsUpdate(link.shortCode, stats.total_clicks);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stats]);

  return (
    <div className={`url-card ${isSelected ? "url-card--selected" : ""}`} onClick={() => onSelect(link.shortCode)}>
      <span className="url-card__icon">
        <Link2 size={16} />
      </span>
      <div className="url-card__main">
        <span className="url-card__short">{link.shortUrl}</span>
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
          <X size={12} />
          Remove
        </button>
      </div>
    </div>
  );
}
