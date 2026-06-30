import { useState } from "react";
import { Link } from "react-router-dom";
import { getUrlStats } from "../api/client";
import { useMyLinks } from "../hooks/useMyLinks";
import { usePolling } from "../hooks/usePolling";
import { UrlCard } from "../components/UrlCard";
import { ClicksOverTimeChart } from "../components/ClicksOverTimeChart";
import { BreakdownPieChart } from "../components/BreakdownPieChart";

export function DashboardPage() {
  const { links, removeLink } = useMyLinks();
  const [selectedCode, setSelectedCode] = useState(links[0]?.shortCode ?? null);

  const { data: selectedStats } = usePolling(
    () => getUrlStats(selectedCode),
    { intervalMs: 5000, enabled: Boolean(selectedCode) },
  );

  if (links.length === 0) {
    return (
      <div className="page">
        <h1>Dashboard</h1>
        <p className="empty-state">
          You haven't shortened any links yet in this browser. <Link to="/">Shorten one →</Link>
        </p>
      </div>
    );
  }

  return (
    <div className="page page--dashboard">
      <h1>Dashboard</h1>
      <div className="dashboard-layout">
        <div className="url-list">
          {links.map((link) => (
            <UrlCard
              key={link.shortCode}
              link={link}
              isSelected={link.shortCode === selectedCode}
              onSelect={setSelectedCode}
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
            <h2>{selectedCode}</h2>
            {!selectedStats ? (
              <p className="empty-state">Loading…</p>
            ) : (
              <>
                {!selectedStats.analytics_available && (
                  <p className="warning-banner">
                    Analytics service is unavailable right now - showing core link info only.
                  </p>
                )}
                <p className="total-clicks">{selectedStats.total_clicks} total clicks</p>

                <h3>Clicks over time</h3>
                <ClicksOverTimeChart hourlyClicks={selectedStats.hourly_clicks} />

                <div className="pie-row">
                  <div>
                    <h3>Device / browser</h3>
                    <BreakdownPieChart
                      data={selectedStats.device_breakdown.map((d) => ({
                        ...d,
                        label: `${d.device_type} / ${d.browser}`,
                      }))}
                      nameKey="label"
                    />
                  </div>
                  <div>
                    <h3>Referrer</h3>
                    <BreakdownPieChart
                      data={selectedStats.referrer_breakdown}
                      nameKey="referrer_domain"
                    />
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
