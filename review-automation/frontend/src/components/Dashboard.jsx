import React from "react";
import TrendChart from "./TrendChart";
import TopicHeatmap from "./TopicHeatmap";
import NPSGauge from "./NPSGauge";

const styles = {
  page: { fontFamily: "'Segoe UI', sans-serif", background: "#f5f7fa", minHeight: "100vh", padding: "24px" },
  header: { marginBottom: "24px" },
  title: { fontSize: "24px", fontWeight: 700, color: "#1a1a2e", margin: 0 },
  subtitle: { fontSize: "14px", color: "#666", marginTop: "4px" },
  badge: { display: "inline-block", fontSize: "11px", background: "#e0f2fe", color: "#0369a1", borderRadius: "4px", padding: "2px 8px" },
  grid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginBottom: "20px" },
  card: { background: "#fff", borderRadius: "12px", padding: "20px", boxShadow: "0 1px 4px rgba(0,0,0,0.08)" },
  cardTitle: { fontSize: "14px", fontWeight: 600, color: "#444", marginBottom: "16px", textTransform: "uppercase", letterSpacing: "0.5px" },
  fullWidth: { gridColumn: "1 / -1" },
};

export default function Dashboard({ trends, heatmap, nps }) {
  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <h1 style={styles.title}>Review Dashboard</h1>
        <p style={styles.subtitle}>Real-time insight into customer feedback</p>
      </div>

      <div style={{ ...styles.grid, gridTemplateColumns: "2fr 1fr" }}>
        <div style={styles.card}>
          <div style={styles.cardTitle}>Sentiment Trends (30 days)</div>
          <TrendChart data={trends} />
        </div>
        <div style={styles.card}>
          <div style={styles.cardTitle}>Net Promoter Score</div>
          <NPSGauge nps={nps} />
        </div>
      </div>

      <div style={styles.card}>
        <div style={styles.cardTitle}>Topic Breakdown by Sentiment</div>
        <TopicHeatmap data={heatmap} />
      </div>
    </div>
  );
}
