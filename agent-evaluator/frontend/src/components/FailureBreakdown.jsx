import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

const COLORS = {
  none: "#10b981",
  hallucination: "#ef4444",
  incomplete_plan: "#f59e0b",
  wrong_tool: "#f97316",
  bad_arguments: "#a855f7",
  off_topic: "#3b82f6",
  format_error: "#64748b",
};

export default function FailureBreakdown({ failures }) {
  const data = Object.entries(failures || {})
    .filter(([, v]) => v > 0)
    .map(([k, v]) => ({ type: k, count: v }));

  return (
    <div>
      <div style={{ fontSize: "14px", fontWeight: 600, color: "#94a3b8", marginBottom: "12px", textTransform: "uppercase", letterSpacing: "0.05em" }}>
        Failure Type Distribution
      </div>
      <div style={{ background: "#1e293b", borderRadius: "8px", padding: "16px" }}>
        {data.length === 0 ? (
          <div style={{ color: "#4b5563", textAlign: "center", padding: "32px 0", fontSize: "14px" }}>
            No failures recorded yet.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data} margin={{ top: 4, right: 8, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis
                dataKey="type"
                tick={{ fill: "#64748b", fontSize: 11 }}
                tickFormatter={(v) => v.replace("_", " ")}
              />
              <YAxis tick={{ fill: "#64748b", fontSize: 11 }} allowDecimals={false} />
              <Tooltip
                contentStyle={{ background: "#0f172a", border: "1px solid #334155", borderRadius: "6px" }}
                labelStyle={{ color: "#94a3b8" }}
                itemStyle={{ color: "#e2e8f0" }}
                cursor={{ fill: "#ffffff08" }}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {data.map((entry) => (
                  <Cell key={entry.type} fill={COLORS[entry.type] || "#64748b"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
