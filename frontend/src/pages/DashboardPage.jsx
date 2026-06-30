import { useCallback, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { BarChart3, Hash, Link2, MousePointerClick, TrendingUp } from "lucide-react";
import { getUrlStats } from "../api/client";
import { useMyLinks } from "../hooks/useMyLinks";
import { usePolling } from "../hooks/usePolling";
import { UrlCard } from "../components/UrlCard";
import { ClicksOverTimeChart } from "../components/ClicksOverTimeChart";
import { BreakdownPieChart } from "../components/BreakdownPieChart";

export function DashboardPage() {
  const { links, removeLink } = useMyLinks();
  const [selectedCode, setSelectedCode] = useState(links[0]?.shortCode ?? null);
  const [clicksByCode, setClicksByCode] = useState({});

  const handleStatsUpdate = useCallback((shortCode, totalClicks) => {
    setClicksByCode((prev) => (prev[shortCode] === totalClicks ? prev : { ...prev, [shortCode]: totalClicks }));
  }, []);

  const totalClicksAcrossLinks = useMemo(
    () => Object.values(clicksByCode).reduce((sum, n) => sum + n, 0),
    [clicksByCode],
  );

  const avgClicksPerLink = links.length > 0 ? (totalClicksAcrossLinks / links.length).toFixed(1) : "0";

  const { data: selectedStats } = usePolling(
    () => getUrlStats(selectedCode),
    { intervalMs: 5000, enabled: Boolean(selectedCode) },
  );

  if (links.length === 0) {
    return (
      <div className="page">
        <div className="page-header">
          <h1>Dashboard</h1>
          <p>Track clicks, devices, and referrers for every link you shorten.</p>
        </div>
        <div className="empty-state-block">
          <BarChart3 size={40} strokeWidth={1.5} />
          <p>You haven't shortened any links yet in this browser.</p>
          <Link to="/">
            <Link2 size={15} />
            Shorten your first link
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="page page--dashboard">
      <div className="page-header page-header--left">
        <h1>Dashboard</h1>
        <p>Live click data, refreshed every 5 seconds.</p>
      </div>

      <div className="summary-row">
        <div className="summary-card">
          <span className="summary-card__icon">
            <Hash size={19} />
          </span>
          <div>
            <div className="summary-card__value">{links.length}</div>
            <div className="summary-card__label">Total links</div>
          </div>
        </div>
        <div className="summary-card">
          <span className="summary-card__icon">
            <MousePointerClick size={19} />
          </span>
          <div>
            <div className="summary-card__value">{totalClicksAcrossLinks}</div>
            <div className="summary-card__label">Total clicks</div>
          </div>
        </div>
        <div className="summary-card">
          <span className="summary-card__icon">
            <TrendingUp size={19} />
          </span>
          <div>
            <div className="summary-card__value">{avgClicksPerLink}</div>
            <div className="summary-card__label">Avg. clicks / link</div>
          </div>
        </div>
      </div>

      <div className="dashboard-layout">
        <div className="url-list">
          {links.map((link) => (
            <UrlCard
              key={link.shortCode}
              link={link}
              isSelected={link.shortCode === selectedCode}
              onSelect={setSelectedCode}
              onStatsUpdate={handleStatsUpdate}
              onRemove={(code) => {
                removeLink(code);
                if (code === selectedCode) {
                  setSelectedCode(null);
                }
              }}
            />
          ))}
        </div>

        {selectedCode && (
          <div className="detail-panel">
            <div className="detail-panel__header">
              <span className="detail-panel__code">
                <Link2 size={15} />
                {selectedCode}
              </span>
            </div>
            {!selectedStats ? (
              <p className="empty-state">Loading…</p>
            ) : (
              <>
                {!selectedStats.analytics_available && (
                  <p className="warning-banner">
                    Analytics service is unavailable right now - showing core link info only.
                  </p>
                )}
                <div className="total-clicks">
                  {selectedStats.total_clicks}
                  <span>total clicks</span>
                </div>

                <h3>Clicks over time</h3>
                <div className="chart-card">
                  <ClicksOverTimeChart hourlyClicks={selectedStats.hourly_clicks} />
                </div>

                <div className="pie-row">
                  <div>
                    <h3>Device / browser</h3>
                    <div className="chart-card">
                      <BreakdownPieChart
                        data={selectedStats.device_breakdown.map((d) => ({
                          ...d,
                          label: `${d.device_type} / ${d.browser}`,
                        }))}
                        nameKey="label"
                      />
                    </div>
                  </div>
                  <div>
                    <h3>Referrer</h3>
                    <div className="chart-card">
                      <BreakdownPieChart
                        data={selectedStats.referrer_breakdown}
                        nameKey="referrer_domain"
                      />
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
