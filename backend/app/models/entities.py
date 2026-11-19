from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.session import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="citizen")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    complaints: Mapped[list["Complaint"]] = relationship(back_populates="citizen")

class Complaint(Base):
    __tablename__ = "complaints"
    id: Mapped[int] = mapped_column(primary_key=True)
    citizen_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    description: Mapped[str] = mapped_column(Text)
    reference: Mapped[str | None] = mapped_column(String(40), unique=True, index=True, nullable=True)
    title: Mapped[str | None] = mapped_column(String(180), nullable=True)
    preferred_language: Mapped[str | None] = mapped_column(String(40), nullable=True)
    detected_language: Mapped[str | None] = mapped_column(String(80), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    original_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    locality: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    landmark: Mapped[str | None] = mapped_column(String(255), nullable=True)
    geocoded_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    location_source: Mapped[str | None] = mapped_column(String(30), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    supporting_information: Mapped[str | None] = mapped_column(Text, nullable=True)
    intent: Mapped[str | None] = mapped_column(String(50), nullable=True)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    urgency: Mapped[str | None] = mapped_column(String(30), nullable=True)
    sentiment: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="Submitted")
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="Normal")
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    citizen: Mapped[User] = relationship(back_populates="complaints")
    predictions: Mapped[list["Prediction"]] = relationship(back_populates="complaint", cascade="all, delete-orphan")
    history: Mapped[list["StatusHistory"]] = relationship(back_populates="complaint", cascade="all, delete-orphan")
    responses: Mapped[list["CitizenResponse"]] = relationship(back_populates="complaint", cascade="all, delete-orphan")
    attachments: Mapped[list["Attachment"]] = relationship(back_populates="complaint", cascade="all, delete-orphan")

Index("ix_complaints_geo", Complaint.latitude, Complaint.longitude)
Index("ix_complaints_category_status", Complaint.category, Complaint.status)

class Prediction(Base):
    __tablename__ = "predictions"
    id: Mapped[int] = mapped_column(primary_key=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), index=True)
    field: Mapped[str] = mapped_column(String(40))
    value: Mapped[str] = mapped_column(String(255))
    confidence: Mapped[str | None] = mapped_column(String(40), nullable=True)
    method: Mapped[str] = mapped_column(String(120))
    human_correction: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    complaint: Mapped[Complaint] = relationship(back_populates="predictions")

class StatusHistory(Base):
    __tablename__ = "status_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), index=True)
    status: Mapped[str] = mapped_column(String(30))
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    complaint: Mapped[Complaint] = relationship(back_populates="history")

class CitizenResponse(Base):
    __tablename__ = "citizen_responses"
    id: Mapped[int] = mapped_column(primary_key=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    complaint: Mapped[Complaint] = relationship(back_populates="responses")

class Attachment(Base):
    __tablename__ = "attachments"
    id: Mapped[int] = mapped_column(primary_key=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"), index=True)
    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    original_filename: Mapped[str] = mapped_column(String(255))
    stored_filename: Mapped[str] = mapped_column(String(255), unique=True)
    media_type: Mapped[str] = mapped_column(String(80))
    size_bytes: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    complaint: Mapped[Complaint] = relationship(back_populates="attachments")
