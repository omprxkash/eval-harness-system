import React, { useState } from "react";

const STATUS_COLORS = {
  pending: "#f59e0b",
  evaluating: "#3b82f6",
  complete: "#10b981",
  failed: "#ef4444",
};

function scoreColor(score) {
  if (score === null || score === undefined) return "#9ca3af";
  if (score >= 0.7) return "#10b981";
  if (score >= 0.4) return "#f59e0b";
  return "#ef4444";
}

const DEFAULT_TRACE = `{
  "agent_id": "my-agent-v1",
  "goal": "research AI trends in healthcare",
  "trace": [
    {"step": "planner", "input": "healthcare AI trends", "output": "plan created", "status": "complete"},
    {"step": "search", "input": "AI healthcare 2025", "output": "found 10 articles", "status": "complete"},
    {"step": "draft", "input": "summarize findings", "output": "", "status": "failed", "error": "timeout"}
  ],
  "final_output": "AI is transforming healthcare through diagnostics and drug discovery."
}`;

export default function RunTable({ runs, onSelect, onSubmitDone }) {
  const [json, setJson] = useState(DEFAULT_TRACE);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    setError("");
    let parsed;
    try {
      parsed = JSON.parse(json);
    } catch {
      setError("Invalid JSON");
      return;
    }
    setSubmitting(true);
    try {
      const res = await fetch("/api/runs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parsed),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      onSubmitDone();
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  };

  const cellStyle = {
    padding: "10px 12px",
    borderBottom: "1px solid #1e293b",
    verticalAlign: "middle",
  };

  const thStyle = {
    ...cellStyle,
    color: "#64748b",
    fontWeight: 600,
    fontSize: "12px",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
    textAlign: "left",
  };

  return (
    <div>
      <div style={{ background: "#1e293b", borderRadius: "8px", padding: "16px", marginBottom: "24px" }}>
        <div style={{ fontSize: "14px", color: "#94a3b8", marginBottom: "8px", fontWeight: 600 }}>
          Submit a trace
        </div>
        <textarea
          value={json}
          onChange={(e) => setJson(e.target.value)}
          rows={10}
          style={{
            width: "100%",
            background: "#0f172a",
            color: "#e2e8f0",
            border: "1px solid #334155",
            borderRadius: "6px",
            padding: "10px",
            fontSize: "13px",
            fontFamily: "monospace",
            resize: "vertical",
            boxSizing: "border-box",
          }}
        />
        {error && <div style={{ color: "#ef4444", fontSize: "13px", marginTop: "4px" }}>{error}</div>}
        <button
          onClick={handleSubmit}
          disabled={submitting}
          style={{
            marginTop: "10px",
            background: "#3b82f6",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
            padding: "8px 20px",
            cursor: submitting ? "not-allowed" : "pointer",
            fontSize: "14px",
            fontWeight: 600,
            opacity: submitting ? 0.7 : 1,
          }}
        >
          {submitting ? "Submitting..." : "Submit"}
        </button>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px" }}>
          <thead>
            <tr style={{ background: "#1e293b" }}>
              <th style={thStyle}>ID</th>
              <th style={thStyle}>Agent ID</th>
              <th style={thStyle}>Goal</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Score</th>
              <th style={thStyle}>Result</th>
              <th style={thStyle}>Submitted</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <tr
                key={run.id}
                onClick={() => onSelect(run)}
                style={{ cursor: "pointer", transition: "background 0.1s" }}
                onMouseEnter={(e) => (e.currentTarget.style.background = "#1e293b")}
                onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
              >
                <td style={cellStyle}>{run.id}</td>
                <td style={cellStyle}>{run.agent_id}</td>
                <td style={cellStyle}>
                  {run.goal.length > 60 ? run.goal.slice(0, 60) + "..." : run.goal}
                </td>
                <td style={cellStyle}>
                  <span
                    style={{
                      background: STATUS_COLORS[run.status] + "22",
                      color: STATUS_COLORS[run.status] || "#9ca3af",
                      padding: "2px 8px",
                      borderRadius: "4px",
                      fontSize: "12px",
                      fontWeight: 600,
                    }}
                  >
                    {run.status}
                  </span>
                </td>
                <td style={{ ...cellStyle, color: scoreColor(run.result?.overall_score) }}>
                  {run.result != null
                    ? `${Math.round(run.result.overall_score * 100)}%`
                    : "-"}
                </td>
                <td style={cellStyle}>
                  {run.result != null ? (
                    <span
                      style={{
                        background: run.result.passed ? "#10b98122" : "#ef444422",
                        color: run.result.passed ? "#10b981" : "#ef4444",
                        padding: "2px 8px",
                        borderRadius: "4px",
                        fontSize: "12px",
                        fontWeight: 600,
                      }}
                    >
                      {run.result.passed ? "PASS" : "FAIL"}
                    </span>
                  ) : "-"}
                </td>
                <td style={{ ...cellStyle, color: "#64748b", fontSize: "12px" }}>
                  {run.submitted_at ? new Date(run.submitted_at).toLocaleString() : "-"}
                </td>
              </tr>
            ))}
            {runs.length === 0 && (
              <tr>
                <td colSpan={7} style={{ ...cellStyle, color: "#4b5563", textAlign: "center", padding: "32px" }}>
                  No runs yet. Submit a trace above.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
