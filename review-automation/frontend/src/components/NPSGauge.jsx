import React from "react";
import { RadialBarChart, RadialBar, ResponsiveContainer, Tooltip } from "recharts";

export default function NPSGauge({ nps }) {
  if (!nps || nps.nps === null) {
    return <p style={{ color: "#999", textAlign: "center", paddingTop: "40px" }}>Not enough data yet.</p>;
  }

  const score = nps.nps;
  const color = score >= 50 ? "#22c55e" : score >= 0 ? "#f59e0b" : "#ef4444";
  const pct = Math.round(((score + 100) / 200) * 100);
  const normalized = Math.min(100, Math.max(0, pct));

  return (
    <div style={{ textAlign: "center" }}>
      <ResponsiveContainer width="100%" height={180}>
        <RadialBarChart
          cx="50%"
          cy="80%"
          innerRadius="60%"
          outerRadius="90%"
          startAngle={180}
          endAngle={0}
          data={[{ name: "NPS", value: normalized, fill: color }]}
        >
          <RadialBar dataKey="value" cornerRadius={6} />
          <Tooltip formatter={(v) => [`${score}`, "NPS"]} />
        </RadialBarChart>
      </ResponsiveContainer>
      <div style={{ fontSize: "36px", fontWeight: 800, color, marginTop: "-20px" }}>{score}</div>
      <div style={{ fontSize: "12px", color: "#888", marginTop: "4px" }}>
        {nps.total} reviews · {nps.promoters} promoters · {nps.detractors} detractors
      </div>
    </div>
  );
}
