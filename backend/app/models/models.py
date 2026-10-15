from datetime import datetime, timezone
import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    Integer,
)
from sqlalchemy.orm import relationship
from app.db.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    user = relationship("User", back_populates="projects")
    submissions = relationship("CodeSubmission", back_populates="project", cascade="all, delete-orphan")


class CodeSubmission(Base):
    __tablename__ = "code_submissions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(255), nullable=False, default="Untitled Snippet")
    code = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    project = relationship("Project", back_populates="submissions")
    analysis_results = relationship("AnalysisResult", back_populates="submission", cascade="all, delete-orphan")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    submission_id = Column(String(36), ForeignKey("code_submissions.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Core complexity outcomes
    time_complexity = Column(String(64), nullable=False)
    space_complexity = Column(String(64), nullable=False)
    confidence = Column(String(32), nullable=False)  # HIGH, MEDIUM, LOW
    complexity_reasoning = Column(Text, nullable=False)

    # Rich analysis details
    statistics = Column(JSON, nullable=False)
    structure = Column(JSON, nullable=False)
    graph_data = Column(JSON, nullable=False)
    detected_patterns = Column(JSON, nullable=False)
    optimization_suggestions = Column(JSON, nullable=False)

    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    submission = relationship("CodeSubmission", back_populates="analysis_results")
