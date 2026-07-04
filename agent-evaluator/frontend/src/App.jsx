import React, { useState, useEffect } from "react";
import MetricsDashboard from "./components/MetricsDashboard";
import FailureBreakdown from "./components/FailureBreakdown";
import RunTable from "./components/RunTable";
import TraceViewer from "./components/TraceViewer";

const TABS = ["Dashboard", "Runs", "Trace"];

export default function App() {
  const [tab, setTab] = useState("Dashboard");
  const [summary, setSummary] = useState(null);
  const [trend, setTrend] = useState([]);
  const [failures, setFailures] = useState({});
  const [runs, setRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);

  const fetchMetrics = async () => {
    try {
      const [sRes, tRes, fRes] = await Promise.all([
        fetch("/api/metrics/summary"),
        fetch("/api/metrics/trend"),
        fetch("/api/metrics/failures"),
      ]);
      const [s, t, f] = await Promise.all([sRes.json(), tRes.json(), fRes.json()]);
      setSummary(s);
      setTrend(t);
      setFailures(f);
    } catch (e) {
      console.error("metrics fetch failed", e);
    }
  };

  const fetchRuns = async () => {
    try {
      const res = await fetch("/api/runs");
      const data = await res.json();
      setRuns(data);
    } catch (e) {
      console.error("runs fetch failed", e);
    }
  };

  useEffect(() => {
    fetchMetrics();
    fetchRuns();
  }, []);

  const handleSelectRun = (run) => {
    setSelectedRun(run);
    setTab("Trace");
  };

  const handleSubmitDone = () => {
    fetchRuns();
    fetchMetrics();
  };

  const headerStyle = {
    background: "#111",
    color: "#fff",
    padding: "16px 24px",
    display: "flex",
    alignItems: "center",
    gap: "32px",
    borderBottom: "1px solid #333",
  };

  const titleStyle = {
    fontSize: "20px",
    fontWeight: 700,
    letterSpacing: "0.5px",
    color: "#e2e8f0",
  };

  const tabStyle = (active) => ({
    background: "none",
    border: "none",
    color: active ? "#60a5fa" : "#9ca3af",
    cursor: "pointer",
    fontSize: "15px",
    fontWeight: active ? 600 : 400,
    padding: "4px 0",
    borderBottom: active ? "2px solid #60a5fa" : "2px solid transparent",
  });

  const bodyStyle = {
    background: "#0f172a",
    minHeight: "calc(100vh - 57px)",
    padding: "24px",
    color: "#e2e8f0",
    fontFamily: "system-ui, sans-serif",
  };

  return (
    <div style={{ fontFamily: "system-ui, sans-serif", background: "#0f172a", minHeight: "100vh" }}>
      <div style={headerStyle}>
        <span style={titleStyle}>Agent Evaluator</span>
        {TABS.map((t) => (
          <button key={t} style={tabStyle(tab === t)} onClick={() => setTab(t)}>
            {t}
          </button>
        ))}
      </div>
      <div style={bodyStyle}>
        {tab === "Dashboard" && (
          <div style={{ display: "flex", gap: "24px", flexWrap: "wrap" }}>
            <div style={{ flex: "1 1 480px" }}>
              <MetricsDashboard summary={summary} trend={trend} />
            </div>
            <div style={{ flex: "1 1 320px" }}>
              <FailureBreakdown failures={failures} />
            </div>
          </div>
        )}
        {tab === "Runs" && (
          <RunTable runs={runs} onSelect={handleSelectRun} onSubmitDone={handleSubmitDone} />
        )}
        {tab === "Trace" && (
          <TraceViewer run={selectedRun} />
        )}
      </div>
    </div>
  );
}
