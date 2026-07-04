import React from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

function StatCard({ label, value }) {
  return (
    <div
      style={{
        background: "#1e293b",
        borderRadius: "8px",
        padding: "16px 20px",
        flex: "1 1 130px",
      }}
    >
      <div style={{ color: "#64748b", fontSize: "12px", fontWeight: 600, textTransform: "uppercase", marginBottom: "6px" }}>
        {label}
      </div>
      <div style={{ color: "#e2e8f0", fontSize: "24px", fontWeight: 700 }}>{value}</div>
    </div>
  );
}

export default function MetricsDashboard({ summary, trend }) {
  const s = summary || {};

  return (
    <div>
      <div style={{ fontSize: "14px", fontWeight: 600, color: "#94a3b8", marginBottom: "12px", textTransform: "uppercase", letterSpacing: "0.05em" }}>
        Summary
      </div>
      <div style={{ display: "flex", gap: "12px", flexWrap: "wrap", marginBottom: "24px" }}>
        <StatCard label="Total Runs" value={s.total_runs ?? 0} />
        <StatCard label="Pass Rate" value={`${s.pass_rate ?? 0}%`} />
        <StatCard label="Avg Score" value={s.avg_overall_score != null ? `${Math.round(s.avg_overall_score * 100)}%` : "0%"} />
        <StatCard label="Hallucination" value={`${s.hallucination_rate ?? 0}%`} />
      </div>

      <div style={{ fontSize: "14px", fontWeight: 600, color: "#94a3b8", marginBottom: "12px", textTransform: "uppercase", letterSpacing: "0.05em" }}>
        Daily Pass Rate (30 days)
      </div>
      <div style={{ background: "#1e293b", borderRadius: "8px", padding: "16px" }}>
        {trend && trend.length > 0 ? (
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={trend} margin={{ top: 4, right: 12, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis
                dataKey="date"
                tick={{ fill: "#64748b", fontSize: 11 }}
                tickFormatter={(v) => v.slice(5)}
              />
              <YAxis
                domain={[0, 100]}
                tick={{ fill: "#64748b", fontSize: 11 }}
                unit="%"
              />
              <Tooltip
                contentStyle={{ background: "#0f172a", border: "1px solid #334155", borderRadius: "6px" }}
                labelStyle={{ color: "#94a3b8" }}
                itemStyle={{ color: "#60a5fa" }}
                formatter={(v) => [`${v}%`, "Pass Rate"]}
              />
              <Line
                type="monotone"
                dataKey="pass_rate"
                stroke="#60a5fa"
                strokeWidth={2}
                dot={{ fill: "#60a5fa", r: 3 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div style={{ color: "#4b5563", textAlign: "center", padding: "32px 0", fontSize: "14px" }}>
            No trend data yet.
          </div>
        )}
      </div>
    </div>
  );
}
