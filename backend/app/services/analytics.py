from datetime import date
from sqlalchemy import and_, func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Alert, Child, Measurement, Referral
from ..utils.who_zscore import calculate_prevalence, classify_risk_level


async def latest_measurements(db: AsyncSession, barangay_id=None):
    subq = (
        select(Measurement.child_id, func.max(Measurement.measurement_date).label("max_date"))
        .join(Child, Child.id == Measurement.child_id)
        .where(Child.is_active.is_(True))
        .group_by(Measurement.child_id)
        .subquery()
    )
    stmt = select(Measurement).options(selectinload(Measurement.child)).join(subq, and_(Measurement.child_id == subq.c.child_id, Measurement.measurement_date == subq.c.max_date))
    if barangay_id:
        stmt = stmt.join(Child, Child.id == Measurement.child_id).where(Child.barangay_id == barangay_id)
    return list((await db.scalars(stmt)).all())


async def summary_for_barangay(db: AsyncSession, barangay_id=None) -> dict:
    child_stmt = select(func.count(Child.id)).where(Child.is_active.is_(True))
    alert_stmt = select(Alert.severity, func.count(Alert.id)).where(Alert.is_resolved.is_(False)).group_by(Alert.severity)
    ref_stmt = select(func.count(Referral.id)).where(Referral.status == "pending")
    if barangay_id:
        child_stmt = child_stmt.where(Child.barangay_id == barangay_id)
        alert_stmt = alert_stmt.join(Child, Child.id == Alert.child_id).where(Child.barangay_id == barangay_id)
        ref_stmt = ref_stmt.join(Child, Child.id == Referral.child_id).where(Child.barangay_id == barangay_id)
    measurements = await latest_measurements(db, barangay_id)
    prevalence = calculate_prevalence(measurements)
    alerts = {str(row[0]): row[1] for row in (await db.execute(alert_stmt)).all()}
    return {
        "total_children": await db.scalar(child_stmt) or 0,
        "total_measured_this_month": len([m for m in measurements if m.measurement_date.month == date.today().month]),
        "prevalence": {
            "stunting": prevalence["stunting_rate"],
            "wasting": prevalence["wasting_rate"],
            "underweight": prevalence["underweight_rate"],
        },
        "active_alerts_count": alerts,
        "pending_referrals_count": await db.scalar(ref_stmt) or 0,
        "risk_level": classify_risk_level(prevalence),
        "risk_level_label": classify_risk_level(prevalence).replace("_", " ").title(),
        "sample_size": prevalence["sample_size"],
    }
