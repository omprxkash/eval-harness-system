import React, { useState, useEffect } from "react";
import Dashboard from "./components/Dashboard";

const API = process.env.REACT_APP_API_URL || "";

export default function App() {
  const [trends, setTrends] = useState([]);
  const [heatmap, setHeatmap] = useState([]);
  const [nps, setNps] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchAll = async () => {
    try {
      const [tRes, hRes, nRes] = await Promise.all([
        fetch(`${API}/analytics/trends`),
        fetch(`${API}/analytics/topic-heatmap`),
        fetch(`${API}/analytics/nps`),
      ]);
      const [tData, hData, nData] = await Promise.all([tRes.json(), hRes.json(), nRes.json()]);
      setTrends(tData.trends || []);
      setHeatmap(hData.heatmap || []);
      setNps(nData);
    } catch (e) {
      console.error("Failed to fetch analytics", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh", fontFamily: "sans-serif" }}>
        Loading…
      </div>
    );
  }

  return <Dashboard trends={trends} heatmap={heatmap} nps={nps} />;
}
