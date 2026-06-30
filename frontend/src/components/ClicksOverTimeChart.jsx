import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

function formatHourLabel(isoString) {
  const date = new Date(isoString);
  return date.toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit" });
}

export function ClicksOverTimeChart({ hourlyClicks }) {
  if (!hourlyClicks || hourlyClicks.length === 0) {
    return <p className="empty-state">No clicks recorded yet.</p>;
  }

  const data = hourlyClicks.map((bucket) => ({
    label: formatHourLabel(bucket.hour_start),
    count: bucket.count,
  }));

  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="label" tick={{ fontSize: 11 }} />
        <YAxis allowDecimals={false} />
        <Tooltip />
        <Bar dataKey="count" fill="#4f46e5" isAnimationActive={false} />
      </BarChart>
    </ResponsiveContainer>
  );
}
