import React from "react";

const SENTIMENTS = ["positive", "neutral", "negative"];
const COLORS = {
  positive: { bg: "#dcfce7", text: "#166534" },
  neutral: { bg: "#fef9c3", text: "#854d0e" },
  negative: { bg: "#fee2e2", text: "#991b1b" },
};

function cell(count, sentiment) {
  if (!count) return { background: "#f9fafb", color: "#e5e7eb" };
  const { bg, text } = COLORS[sentiment];
  return { background: bg, color: text, fontWeight: 600 };
}

export default function TopicHeatmap({ data }) {
  if (!data || data.length === 0) {
    return <p style={{ color: "#999" }}>No topic data yet.</p>;
  }

  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
        <thead>
          <tr>
            <th style={{ textAlign: "left", padding: "8px 12px", color: "#666", fontWeight: 600 }}>Topic</th>
            {SENTIMENTS.map((s) => (
              <th key={s} style={{ padding: "8px 12px", textAlign: "center", color: "#666", fontWeight: 600, textTransform: "capitalize" }}>{s}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.topic}>
              <td style={{ padding: "8px 12px", color: "#333", fontWeight: 500, textTransform: "capitalize" }}>
                {row.topic.replace(/_/g, " ")}
              </td>
              {SENTIMENTS.map((s) => (
                <td key={s} style={{ padding: "8px 12px", textAlign: "center", borderRadius: "4px", ...cell(row[s], s) }}>
                  {row[s] || 0}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
