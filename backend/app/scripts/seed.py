import asyncio
import random
from datetime import date, timedelta
from sqlalchemy import select
from shapely.geometry import MultiPolygon, Polygon
from app.database import AsyncSessionLocal, init_db
from app.models import Alert, Barangay, Child, Measurement, Purok, Referral, User
from app.models.entities import Priority, ReferralStatus, Sex, UserRole
from app.services.alerts import alerts_for_measurement
from app.utils.security import hash_password
from app.utils.who_zscore import calculate_full_assessment


BARANGAYS = [
    "Antonio Luna", "Bay-ang", "Bayabas", "Caasinan", "Cabinet", "Calamba",
    "Calibunan", "Comagascas", "Concepcion", "Del Pilar", "Katugasan",
    "Kauswagan", "La Union", "Mabini", "Mahaba",
]


def polygon_for(index: int):
    base_lat, base_lng = 9.1833, 125.5333
    row, col = divmod(index, 5)
    lat = base_lat + (row - 1) * 0.018
    lng = base_lng + (col - 2) * 0.018
    poly = Polygon([(lng, lat), (lng + 0.014, lat), (lng + 0.014, lat + 0.014), (lng, lat + 0.014), (lng, lat)])
    return MultiPolygon([poly]).__geo_interface__, lat + 0.007, lng + 0.007


async def main():
    await init_db()
    async with AsyncSessionLocal() as db:
        existing = await db.scalar(select(User).where(User.username == "superadmin"))
        if existing:
            # If seed was already run previously, ensure seeded users have valid emails.
            updated = False
            if existing.email and existing.email.endswith("@hms.local"):
                existing.email = existing.email.replace("@hms.local", "@example.com")
                db.add(existing)
                updated = True
            admins = list((await db.scalars(select(User).where(User.username.like("admin_brgy%")))).all())
            for u in admins:
                if u.email and u.email.endswith("@hms.local"):
                    u.email = u.email.replace("@hms.local", "@example.com")
                    db.add(u)
                    updated = True
            if updated:
                await db.commit()
                print("Updated existing seeded user emails to @example.com")
            else:
                print("Seed data already exists.")
            return

        barangays = []
        puroks = []
        for i, name in enumerate(BARANGAYS):
            geom, lat, lng = polygon_for(i)
            b = Barangay(name=name, code=f"BRGY-{i+1:02d}", geometry=geom, population_count=random.randint(1800, 6200))
            db.add(b)
            await db.flush()
            barangays.append((b, lat, lng))
            for p in range(1, 5):
                purok = Purok(name=f"Purok {p}", code=f"{b.code}-P{p}", barangay_id=b.id)
                db.add(purok)
                puroks.append(purok)

        superadmin = User(username="superadmin", email="superadmin@example.com", password_hash=hash_password("Admin@123"), role=UserRole.super_admin)
        db.add(superadmin)
        await db.flush()
        for i, (barangay, _, _) in enumerate(barangays, start=1):
            db.add(User(username=f"admin_brgy{i}", email=f"admin_brgy{i}@example.com", password_hash=hash_password("Admin@123"), role=UserRole.admin, barangay_id=barangay.id))
        await db.flush()

        all_puroks = list((await db.scalars(select(Purok))).all())
        names = ["Ana", "Ben", "Carla", "Dino", "Ella", "Finn", "Gina", "Hugo", "Iris", "Joel"]
        for i in range(50):
            barangay, lat, lng = random.choice(barangays)
            p = random.choice([x for x in all_puroks if x.barangay_id == barangay.id])
            birth = date.today() - timedelta(days=random.randint(180, 60 * 30))
            child = Child(
                full_name=f"{random.choice(names)} Sample {i+1}",
                birth_date=birth,
                sex=random.choice([Sex.male, Sex.female]),
                guardian_name=f"Guardian {i+1}",
                contact_number="09" + "".join(random.choice("0123456789") for _ in range(9)),
                purok_id=p.id,
                barangay_id=barangay.id,
                latitude=lat + random.uniform(-0.005, 0.005),
                longitude=lng + random.uniform(-0.005, 0.005),
            )
            db.add(child)
            await db.flush()
            for n in range(3):
                mdate = date.today() - timedelta(days=180 - n * 60)
                age = max(1, (mdate.year - birth.year) * 12 + mdate.month - birth.month)
                malnourished = i % 5 == 0 or i % 3 == 0
                height = 52 + age * 1.05 + random.uniform(-3, 3)
                weight = 3.5 + age * 0.25 + random.uniform(-1, 1)
                if malnourished:
                    weight *= 0.72 if i % 5 == 0 else 0.84
                assessment = calculate_full_assessment(child.sex.value, age, weight, height)
                m = Measurement(child_id=child.id, measured_by=superadmin.id, measurement_date=mdate, age_in_months=age, weight_kg=round(weight, 2), height_cm=round(height, 1), muac_cm=round(random.uniform(10, 15), 1), **assessment)
                db.add(m)
                await db.flush()
            for alert in alerts_for_measurement(child, m):
                db.add(alert)
                if alert.severity.value in {"critical", "high"}:
                    db.add(Referral(child_id=child.id, referred_by=superadmin.id, referred_to="Cabadbaran City Health Office", reason=alert.message, status=ReferralStatus.pending, priority=Priority.urgent))
        await db.commit()
        print("Seed complete. Login with superadmin / Admin@123")


if __name__ == "__main__":
    asyncio.run(main())
