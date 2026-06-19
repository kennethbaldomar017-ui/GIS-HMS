import enum
import uuid
from datetime import date, datetime
from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class UserRole(str, enum.Enum):
    super_admin = "super_admin"
    admin = "admin"


class Sex(str, enum.Enum):
    male = "male"
    female = "female"


class WazStatus(str, enum.Enum):
    severely_underweight = "severely_underweight"
    underweight = "underweight"
    normal = "normal"
    overweight = "overweight"


class HazStatus(str, enum.Enum):
    severely_stunted = "severely_stunted"
    stunted = "stunted"
    normal = "normal"
    tall = "tall"


class WhzStatus(str, enum.Enum):
    severely_wasted = "severely_wasted"
    wasted = "wasted"
    normal = "normal"
    overweight = "overweight"
    obese = "obese"


class OverallStatus(str, enum.Enum):
    severe_acute_malnutrition = "severe_acute_malnutrition"
    moderate_acute_malnutrition = "moderate_acute_malnutrition"
    normal = "normal"
    overweight = "overweight"


class AlertType(str, enum.Enum):
    severe_wasting = "severe_wasting"
    severe_stunting = "severe_stunting"
    severe_underweight = "severe_underweight"
    high_prevalence = "high_prevalence"
    deteriorating = "deteriorating"


class Severity(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class ReferralStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    completed = "completed"
    cancelled = "cancelled"


class Priority(str, enum.Enum):
    emergency = "emergency"
    urgent = "urgent"
    routine = "routine"


class ReportType(str, enum.Enum):
    monthly = "monthly"
    quarterly = "quarterly"
    annual = "annual"
    custom = "custom"


class ReportStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"


class JobStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


def uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Barangay(Base):
    __tablename__ = "barangays"
    id = uuid_pk()
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    code: Mapped[str] = mapped_column(String(40), unique=True)
    geometry: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    population_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    puroks = relationship("Purok", back_populates="barangay")


class Purok(Base):
    __tablename__ = "puroks"
    id = uuid_pk()
    name: Mapped[str] = mapped_column(String(120), index=True)
    code: Mapped[str] = mapped_column(String(40), index=True)
    barangay_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("barangays.id"))
    geometry: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    barangay = relationship("Barangay", back_populates="puroks")


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id = uuid_pk()
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.admin)
    barangay_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("barangays.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    barangay = relationship("Barangay")


class Child(Base, TimestampMixin):
    __tablename__ = "children"
    id = uuid_pk()
    full_name: Mapped[str] = mapped_column(String(180), index=True)
    birth_date: Mapped[date] = mapped_column(Date)
    sex: Mapped[Sex] = mapped_column(Enum(Sex))
    guardian_name: Mapped[str] = mapped_column(String(180))
    contact_number: Mapped[str | None] = mapped_column(String(40), nullable=True)
    purok_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("puroks.id"))
    barangay_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("barangays.id"))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    barangay = relationship("Barangay")
    purok = relationship("Purok")
    measurements = relationship("Measurement", back_populates="child", cascade="all, delete-orphan")


class Measurement(Base):
    __tablename__ = "measurements"
    id = uuid_pk()
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id"))
    measured_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    measurement_date: Mapped[date] = mapped_column(Date, index=True)
    age_in_months: Mapped[int] = mapped_column(Integer)
    weight_kg: Mapped[float] = mapped_column(Float)
    height_cm: Mapped[float] = mapped_column(Float)
    muac_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    waz: Mapped[float] = mapped_column(Float)
    haz: Mapped[float] = mapped_column(Float)
    whz: Mapped[float] = mapped_column(Float)
    waz_status: Mapped[WazStatus] = mapped_column(Enum(WazStatus))
    haz_status: Mapped[HazStatus] = mapped_column(Enum(HazStatus))
    whz_status: Mapped[WhzStatus] = mapped_column(Enum(WhzStatus))
    overall_status: Mapped[OverallStatus] = mapped_column(Enum(OverallStatus))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    child = relationship("Child", back_populates="measurements")
    user = relationship("User")


class Alert(Base):
    __tablename__ = "alerts"
    id = uuid_pk()
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id"))
    measurement_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("measurements.id"), nullable=True)
    alert_type: Mapped[AlertType] = mapped_column(Enum(AlertType))
    severity: Mapped[Severity] = mapped_column(Enum(Severity))
    message: Mapped[str] = mapped_column(Text)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    child = relationship("Child")
    measurement = relationship("Measurement")


class Referral(Base):
    __tablename__ = "referrals"
    id = uuid_pk()
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id"))
    referred_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    referred_to: Mapped[str] = mapped_column(Text)
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[ReferralStatus] = mapped_column(Enum(ReferralStatus), default=ReferralStatus.pending)
    priority: Mapped[Priority] = mapped_column(Enum(Priority), default=Priority.routine)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    referred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    child = relationship("Child")


class Report(Base):
    __tablename__ = "reports"
    id = uuid_pk()
    title: Mapped[str] = mapped_column(String(220))
    report_type: Mapped[ReportType] = mapped_column(Enum(ReportType))
    barangay_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("barangays.id"), nullable=True)
    generated_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    status: Mapped[ReportStatus] = mapped_column(Enum(ReportStatus), default=ReportStatus.draft)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    data: Mapped[dict] = mapped_column(JSONB, default=dict)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = uuid_pk()
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(120), index=True)
    resource_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    details: Mapped[dict] = mapped_column(JSONB, default=dict)
    ip_address: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BulkImportJob(Base):
    __tablename__ = "bulk_import_jobs"
    id = uuid_pk()
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    file_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.pending)
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    success_rows: Mapped[int] = mapped_column(Integer, default=0)
    error_rows: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[list] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
