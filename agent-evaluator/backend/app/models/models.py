from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class EvalRun(Base):
    __tablename__ = "eval_runs"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(100), nullable=False)
    goal = Column(Text, nullable=False)
    trace = Column(JSON, nullable=False)
    final_output = Column(Text, nullable=False)
    status = Column(String(20), default="pending")
    submitted_at = Column(DateTime, server_default=func.now())

    result = relationship("EvalResult", back_populates="run", uselist=False)


class EvalResult(Base):
    __tablename__ = "eval_results"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("eval_runs.id"), nullable=False)
    task_completion_score = Column(Float, nullable=False)
    step_accuracy_score = Column(Float, nullable=False)
    hallucination_detected = Column(Boolean, default=False)
    overall_score = Column(Float, nullable=False)
    passed = Column(Boolean, nullable=False)
    failure_type = Column(String(50), nullable=True)
    correction = Column(JSON, nullable=True)
    geval_scores = Column(JSON, nullable=True)
    geval_weighted = Column(Float, nullable=True)
    evaluated_at = Column(DateTime, server_default=func.now())

    run = relationship("EvalRun", back_populates="result")
