import React, { useState } from "react";

const STATUS_ICON = {
  complete: "✓",
  failed: "✗",
};

const STATUS_COLOR = {
  complete: "#10b981",
  failed: "#ef4444",
};

const FAILURE_BADGE_COLOR = {
  none: "#10b981",
  hallucination: "#ef4444",
  incomplete_plan: "#f59e0b",
  wrong_tool: "#f97316",
  bad_arguments: "#a855f7",
  off_topic: "#3b82f6",
  format_error: "#64748b",
};

function ScoreBar({ label, value }) {
  const pct = Math.round((value || 0) * 100);
  const color = pct >= 70 ? "#10b981" : pct >= 40 ? "#f59e0b" : "#ef4444";
  return (
    <div style={{ marginBottom: "10px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", marginBottom: "4px" }}>
        <span style={{ color: "#94a3b8" }}>{label}</span>
        <span style={{ color, fontWeight: 600 }}>{pct}%</span>
      </div>
      <div style={{ background: "#1e293b", borderRadius: "4px", height: "6px" }}>
        <div style={{ width: `${pct}%`, background: color, borderRadius: "4px", height: "6px", transition: "width 0.3s" }} />
      </div>
    </div>
  );
}

function StepCard({ step }) {
  const [open, setOpen] = useState(false);
  const status = step.status || "unknown";
  const color = STATUS_COLOR[status] || "#64748b";

  return (
    <div
      style={{
        background: "#1e293b",
        borderRadius: "8px",
        padding: "12px 16px",
        marginBottom: "10px",
        borderLeft: `3px solid ${color}`,
      }}
    >
      <div
        style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer" }}
        onClick={() => setOpen((o) => !o)}
      >
        <span style={{ color, fontWeight: 700, fontSize: "16px" }}>
          {STATUS_ICON[status] || "·"}
        </span>
        <span style={{ fontWeight: 600, fontSize: "14px", color: "#e2e8f0" }}>{step.step}</span>
        <span
          style={{
            marginLeft: "auto",
            fontSize: "12px",
            color,
            background: color + "22",
            padding: "2px 8px",
            borderRadius: "4px",
          }}
        >
          {status}
        </span>
        <span style={{ color: "#4b5563", fontSize: "13px" }}>{open ? "▲" : "▼"}</span>
      </div>
      {step.error && (
        <div style={{ marginTop: "6px", fontSize: "12px", color: "#ef4444" }}>
          Error: {step.error}
        </div>
      )}
      {open && (
        <div style={{ marginTop: "10px", fontSize: "13px" }}>
          {step.input && (
            <div style={{ marginBottom: "6px" }}>
              <span style={{ color: "#64748b", fontWeight: 600 }}>Input: </span>
              <span style={{ color: "#94a3b8" }}>{step.input}</span>
            </div>
          )}
          {step.output && (
            <div>
              <span style={{ color: "#64748b", fontWeight: 600 }}>Output: </span>
              <span style={{ color: "#94a3b8" }}>{step.output}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function TraceViewer({ run }) {
  if (!run) {
    return (
      <div style={{ color: "#4b5563", textAlign: "center", paddingTop: "60px", fontSize: "15px" }}>
        Select a run from the Runs tab to view its trace.
      </div>
    );
  }

  const r = run.result;

  return (
    <div style={{ display: "flex", gap: "24px", flexWrap: "wrap" }}>
      <div style={{ flex: "1 1 360px" }}>
        <div style={{ color: "#64748b", fontSize: "12px", fontWeight: 600, textTransform: "uppercase", marginBottom: "8px" }}>
          Trace — {run.agent_id}
        </div>
        <div style={{ color: "#94a3b8", fontSize: "13px", marginBottom: "16px" }}>
          <span style={{ color: "#64748b" }}>Goal: </span>{run.goal}
        </div>
        {(run.trace || []).map((step, i) => (
          <StepCard key={i} step={step} />
        ))}
        <div style={{ marginTop: "16px", background: "#1e293b", borderRadius: "8px", padding: "14px 16px" }}>
          <div style={{ color: "#64748b", fontSize: "12px", fontWeight: 600, textTransform: "uppercase", marginBottom: "6px" }}>
            Final Output
          </div>
          <div style={{ color: "#e2e8f0", fontSize: "13px", lineHeight: 1.6 }}>{run.final_output}</div>
        </div>
      </div>

      <div style={{ flex: "0 1 300px" }}>
        <div style={{ color: "#64748b", fontSize: "12px", fontWeight: 600, textTransform: "uppercase", marginBottom: "8px" }}>
          Eval Result
        </div>
        {!r ? (
          <div style={{ color: "#4b5563", fontSize: "13px" }}>
            {run.status === "evaluating" ? "Evaluating..." : "No result yet."}
          </div>
        ) : (
          <div>
            <div style={{ marginBottom: "16px" }}>
              <ScoreBar label="Task Completion" value={r.task_completion_score} />
              <ScoreBar label="Step Accuracy" value={r.step_accuracy_score} />
              <ScoreBar label="Overall Score" value={r.overall_score} />
            </div>
            <div style={{ display: "flex", gap: "10px", marginBottom: "16px", flexWrap: "wrap" }}>
              <span
                style={{
                  background: r.passed ? "#10b98122" : "#ef444422",
                  color: r.passed ? "#10b981" : "#ef4444",
                  padding: "4px 12px",
                  borderRadius: "6px",
                  fontWeight: 700,
                  fontSize: "13px",
                }}
              >
                {r.passed ? "PASS" : "FAIL"}
              </span>
              {r.hallucination_detected && (
                <span
                  style={{
                    background: "#ef444422",
                    color: "#ef4444",
                    padding: "4px 12px",
                    borderRadius: "6px",
                    fontSize: "13px",
                    fontWeight: 600,
                  }}
                >
                  Hallucination
                </span>
              )}
            </div>
            <div style={{ marginBottom: "12px" }}>
              <div style={{ color: "#64748b", fontSize: "12px", fontWeight: 600, marginBottom: "4px" }}>
                Failure Type
              </div>
              <span
                style={{
                  background: (FAILURE_BADGE_COLOR[r.failure_type] || "#64748b") + "22",
                  color: FAILURE_BADGE_COLOR[r.failure_type] || "#64748b",
                  padding: "3px 10px",
                  borderRadius: "4px",
                  fontSize: "13px",
                  fontWeight: 600,
                }}
              >
                {r.failure_type || "none"}
              </span>
            </div>
            {r.correction && (
              <div
                style={{
                  background: "#1e293b",
                  borderRadius: "8px",
                  padding: "12px 14px",
                  borderLeft: "3px solid #3b82f6",
                }}
              >
                <div style={{ color: "#64748b", fontSize: "12px", fontWeight: 600, marginBottom: "6px" }}>
                  Correction Suggestion
                </div>
                <div style={{ color: "#94a3b8", fontSize: "12px", marginBottom: "6px" }}>
                  <span style={{ color: "#64748b" }}>Target: </span>{r.correction.target}
                </div>
                <div style={{ color: "#e2e8f0", fontSize: "13px", lineHeight: 1.6 }}>
                  {r.correction.suggestion}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
