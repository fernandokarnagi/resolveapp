"""
Seed script: Mappletree Business City, Singapore sample data.
Run: source venv/bin/activate && python seed.py
"""
import asyncio
from datetime import date, timedelta, datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

TODAY = date.today()


def d(offset=0):
    return (TODAY + timedelta(days=offset)).isoformat()


async def seed():
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]

    # ── Clear existing data (preserve users) ─────────────────────────
    for col in ["buildings", "floors", "units", "vendors",
                "cleaning_schedules", "preventive_maintenance",
                "corrective_maintenance", "cases", "costs",
                "roster", "attendance"]:
        await db[col].delete_many({})
    print("Cleared existing data.")

    # ── Building ──────────────────────────────────────────────────────
    res = await db.buildings.insert_one({
        "name": "Mappletree Business City",
        "address": "20 Pasir Panjang Road, Singapore 117439",
        "total_floors": 10,
        "status": "active",
        "description": "Grade-A business park campus by Mapletree Investments, "
                       "comprising office, retail, and ancillary facilities.",
    })
    bids = str(res.inserted_id)
    print(f"Building: {bids}")

    # ── Floors ────────────────────────────────────────────────────────
    floors_raw = [
        {"floor_number": 1,  "name": "Ground Floor – Retail & Lobby",  "total_units": 5},
        {"floor_number": 2,  "name": "Level 2 – F&B & Amenities",      "total_units": 4},
        {"floor_number": 3,  "name": "Level 3 – Office (East Wing)",    "total_units": 6},
        {"floor_number": 4,  "name": "Level 4 – Office (West Wing)",    "total_units": 6},
        {"floor_number": 5,  "name": "Level 5 – Office (North Wing)",   "total_units": 5},
        {"floor_number": 6,  "name": "Level 6 – Office (South Wing)",   "total_units": 5},
        {"floor_number": 7,  "name": "Level 7 – Office",                "total_units": 4},
        {"floor_number": 8,  "name": "Level 8 – Office",                "total_units": 4},
        {"floor_number": 9,  "name": "Level 9 – Conference & Events",   "total_units": 4},
        {"floor_number": 10, "name": "Level 10 – Rooftop & M&E",       "total_units": 3},
    ]
    fids = {}   # floor_number → str id
    for f in floors_raw:
        f["building_id"] = bids
        r = await db.floors.insert_one(f)
        fids[f["floor_number"]] = str(r.inserted_id)
    print(f"Floors: {len(fids)}")

    # ── Units ─────────────────────────────────────────────────────────
    # Each unit carries a lookup key (floor_number, unit_number) → str id
    units_raw = [
        # ── Ground Floor ──
        {"fn": 1, "unit_number": "G-01",  "type": "commercial",  "status": "occupied",    "area_sqft": 2500, "tenant_name": "Guardian Pharmacy",   "tenant_contact": "+65 6123 4001"},
        {"fn": 1, "unit_number": "G-02",  "type": "commercial",  "status": "occupied",    "area_sqft": 1800, "tenant_name": "Toast Box Café",       "tenant_contact": "+65 6123 4002"},
        {"fn": 1, "unit_number": "G-03",  "type": "commercial",  "status": "vacant",      "area_sqft": 1500, "tenant_name": None,                   "tenant_contact": None},
        {"fn": 1, "unit_number": "G-04",  "type": "commercial",  "status": "occupied",    "area_sqft": 3200, "tenant_name": "DBS Bank Branch",      "tenant_contact": "+65 6123 4004"},
        {"fn": 1, "unit_number": "G-LBY", "type": "common",      "status": "occupied",    "area_sqft": 4500, "tenant_name": "Main Lobby",           "tenant_contact": None},
        # ── Level 2 ──
        {"fn": 2, "unit_number": "L2-01", "type": "commercial",  "status": "occupied",    "area_sqft": 3000, "tenant_name": "Koufu Food Court",     "tenant_contact": "+65 6123 4201"},
        {"fn": 2, "unit_number": "L2-02", "type": "commercial",  "status": "occupied",    "area_sqft": 1200, "tenant_name": "Starbucks",            "tenant_contact": "+65 6123 4202"},
        {"fn": 2, "unit_number": "L2-03", "type": "commercial",  "status": "vacant",      "area_sqft": 2000, "tenant_name": None,                   "tenant_contact": None},
        {"fn": 2, "unit_number": "L2-WC", "type": "common",      "status": "occupied",    "area_sqft":  400, "tenant_name": "L2 Common Washroom",   "tenant_contact": None},
        # ── Level 3 ──
        {"fn": 3, "unit_number": "L3-01", "type": "residential", "status": "occupied",    "area_sqft": 5000, "tenant_name": "Accenture Pte Ltd",    "tenant_contact": "+65 6234 5001"},
        {"fn": 3, "unit_number": "L3-02", "type": "residential", "status": "occupied",    "area_sqft": 4800, "tenant_name": "Bosch Singapore",      "tenant_contact": "+65 6234 5002"},
        {"fn": 3, "unit_number": "L3-03", "type": "residential", "status": "vacant",      "area_sqft": 4500, "tenant_name": None,                   "tenant_contact": None},
        {"fn": 3, "unit_number": "L3-04", "type": "residential", "status": "occupied",    "area_sqft": 6000, "tenant_name": "HP Inc Singapore",     "tenant_contact": "+65 6234 5004"},
        {"fn": 3, "unit_number": "L3-SR", "type": "common",      "status": "occupied",    "area_sqft":  600, "tenant_name": "Server Room L3",       "tenant_contact": None},
        {"fn": 3, "unit_number": "L3-WC", "type": "common",      "status": "occupied",    "area_sqft":  400, "tenant_name": "L3 Common Washroom",   "tenant_contact": None},
        # ── Level 4 ──
        {"fn": 4, "unit_number": "L4-01", "type": "residential", "status": "occupied",    "area_sqft": 5500, "tenant_name": "Siemens Pte Ltd",      "tenant_contact": "+65 6345 1001"},
        {"fn": 4, "unit_number": "L4-02", "type": "residential", "status": "occupied",    "area_sqft": 4800, "tenant_name": "Philips Electronics",  "tenant_contact": "+65 6345 1002"},
        {"fn": 4, "unit_number": "L4-03", "type": "residential", "status": "maintenance", "area_sqft": 4200, "tenant_name": None,                   "tenant_contact": None},
        {"fn": 4, "unit_number": "L4-04", "type": "residential", "status": "occupied",    "area_sqft": 5000, "tenant_name": "3M Singapore",         "tenant_contact": "+65 6345 1004"},
        {"fn": 4, "unit_number": "L4-05", "type": "residential", "status": "vacant",      "area_sqft": 3800, "tenant_name": None,                   "tenant_contact": None},
        {"fn": 4, "unit_number": "L4-WC", "type": "common",      "status": "occupied",    "area_sqft":  400, "tenant_name": "L4 Common Washroom",   "tenant_contact": None},
        # ── Level 5 ──
        {"fn": 5, "unit_number": "L5-01", "type": "residential", "status": "occupied",    "area_sqft": 7200, "tenant_name": "Grab Holdings",        "tenant_contact": "+65 6345 6001"},
        {"fn": 5, "unit_number": "L5-02", "type": "residential", "status": "maintenance", "area_sqft": 3500, "tenant_name": None,                   "tenant_contact": None},
        {"fn": 5, "unit_number": "L5-03", "type": "residential", "status": "occupied",    "area_sqft": 4000, "tenant_name": "Shopee (SEA Ltd)",     "tenant_contact": "+65 6345 6003"},
        {"fn": 5, "unit_number": "L5-MR", "type": "common",      "status": "occupied",    "area_sqft":  800, "tenant_name": "L5 Meeting Room",      "tenant_contact": None},
        {"fn": 5, "unit_number": "L5-WC", "type": "common",      "status": "occupied",    "area_sqft":  400, "tenant_name": "L5 Common Washroom",   "tenant_contact": None},
        # ── Level 6 ──
        {"fn": 6, "unit_number": "L6-01", "type": "residential", "status": "occupied",    "area_sqft": 6000, "tenant_name": "Google Singapore",     "tenant_contact": "+65 6789 1001"},
        {"fn": 6, "unit_number": "L6-02", "type": "residential", "status": "occupied",    "area_sqft": 5500, "tenant_name": "Amazon Web Services",  "tenant_contact": "+65 6789 1002"},
        {"fn": 6, "unit_number": "L6-03", "type": "residential", "status": "vacant",      "area_sqft": 4800, "tenant_name": None,                   "tenant_contact": None},
        {"fn": 6, "unit_number": "L6-SR", "type": "common",      "status": "occupied",    "area_sqft":  600, "tenant_name": "Server Room L6",       "tenant_contact": None},
        {"fn": 6, "unit_number": "L6-WC", "type": "common",      "status": "occupied",    "area_sqft":  400, "tenant_name": "L6 Common Washroom",   "tenant_contact": None},
        # ── Level 7 ──
        {"fn": 7, "unit_number": "L7-01", "type": "residential", "status": "occupied",    "area_sqft": 8000, "tenant_name": "Deloitte Singapore",   "tenant_contact": "+65 6224 8288"},
        {"fn": 7, "unit_number": "L7-02", "type": "residential", "status": "occupied",    "area_sqft": 7500, "tenant_name": "PwC Singapore",        "tenant_contact": "+65 6236 3388"},
        {"fn": 7, "unit_number": "L7-03", "type": "residential", "status": "vacant",      "area_sqft": 4500, "tenant_name": None,                   "tenant_contact": None},
        {"fn": 7, "unit_number": "L7-WC", "type": "common",      "status": "occupied",    "area_sqft":  400, "tenant_name": "L7 Common Washroom",   "tenant_contact": None},
        # ── Level 8 ──
        {"fn": 8, "unit_number": "L8-01", "type": "residential", "status": "occupied",    "area_sqft": 9000, "tenant_name": "EY Singapore",         "tenant_contact": "+65 6535 7777"},
        {"fn": 8, "unit_number": "L8-02", "type": "residential", "status": "occupied",    "area_sqft": 6000, "tenant_name": "KPMG Singapore",       "tenant_contact": "+65 6213 3388"},
        {"fn": 8, "unit_number": "L8-03", "type": "residential", "status": "vacant",      "area_sqft": 5000, "tenant_name": None,                   "tenant_contact": None},
        {"fn": 8, "unit_number": "L8-WC", "type": "common",      "status": "occupied",    "area_sqft":  400, "tenant_name": "L8 Common Washroom",   "tenant_contact": None},
        # ── Level 9 ──
        {"fn": 9, "unit_number": "L9-CR1","type": "common",      "status": "occupied",    "area_sqft": 1800, "tenant_name": "Conference Room A",    "tenant_contact": None},
        {"fn": 9, "unit_number": "L9-CR2","type": "common",      "status": "occupied",    "area_sqft": 1200, "tenant_name": "Conference Room B",    "tenant_contact": None},
        {"fn": 9, "unit_number": "L9-CR3","type": "common",      "status": "occupied",    "area_sqft":  900, "tenant_name": "Conference Room C",    "tenant_contact": None},
        {"fn": 9, "unit_number": "L9-EVT","type": "common",      "status": "occupied",    "area_sqft": 5000, "tenant_name": "Events Hall",          "tenant_contact": None},
        # ── Level 10 ──
        {"fn": 10,"unit_number": "L10-ME","type": "common",      "status": "maintenance", "area_sqft": 2000, "tenant_name": "M&E Plant Room",       "tenant_contact": None},
        {"fn": 10,"unit_number": "L10-RT","type": "common",      "status": "occupied",    "area_sqft": 3500, "tenant_name": "Rooftop Garden",       "tenant_contact": None},
        {"fn": 10,"unit_number": "L10-WT","type": "common",      "status": "occupied",    "area_sqft":  800, "tenant_name": "Water Tank Room",      "tenant_contact": None},
    ]
    uids = {}   # unit_number → str id
    for u in units_raw:
        fn = u.pop("fn")
        u["floor_id"]   = fids[fn]
        u["building_id"] = bids
        r = await db.units.insert_one(u)
        uids[u["unit_number"]] = str(r.inserted_id)
    print(f"Units: {len(uids)}")

    # ── Vendors ───────────────────────────────────────────────────────
    vendors_raw = [
        {"name": "CleanPro Services Pte Ltd",  "type": "cleaning",    "contact_person": "Tan Wei Ming",    "phone": "+65 8100 2001", "email": "ops@cleanpro.sg",        "address": "18 Tuas Ave 5, S639340",          "status": "active", "contract_start": "2024-01-01", "contract_end": "2026-12-31", "hourly_rate": 18.50},
        {"name": "SparkClean International",   "type": "cleaning",    "contact_person": "Lim Hui Ling",    "phone": "+65 8200 3002", "email": "hello@sparkclean.sg",    "address": "30 Jalan Buroh, S619493",         "status": "active", "contract_start": "2024-06-01", "contract_end": "2025-12-31", "hourly_rate": 16.00},
        {"name": "TechFix Engineering Pte Ltd","type": "maintenance", "contact_person": "Rajesh Kumar",    "phone": "+65 9100 4001", "email": "service@techfix.sg",     "address": "12 Woodlands Link, S738733",      "status": "active", "contract_start": "2023-07-01", "contract_end": "2026-06-30", "hourly_rate": 65.00},
        {"name": "Kone Elevator Services",     "type": "maintenance", "contact_person": "David Ng",        "phone": "+65 6300 5000", "email": "sg.support@kone.com",    "address": "2 Kallang Ave #07-18, S339407",   "status": "active", "contract_start": "2022-01-01", "contract_end": "2027-12-31", "hourly_rate": 120.00},
        {"name": "SecureGuard Asia Pte Ltd",   "type": "security",    "contact_person": "Mohammad Farid",  "phone": "+65 8300 6001", "email": "ops@secureguard.sg",     "address": "8 Admiralty St, S757438",         "status": "active", "contract_start": "2024-01-01", "contract_end": "2025-12-31", "hourly_rate": 22.00},
        {"name": "Certis CISCO Security",      "type": "security",    "contact_person": "Ng Boon Kiat",    "phone": "+65 6888 7000", "email": "info@certiscisco.com.sg","address": "1 Certis CISCO Centre, S488922",  "status": "active", "contract_start": "2023-01-01", "contract_end": "2026-12-31", "hourly_rate": 25.00},
    ]
    vids = {}
    for v in vendors_raw:
        r = await db.vendors.insert_one(v)
        vids[v["name"]] = str(r.inserted_id)
    print(f"Vendors: {len(vids)}")

    cleanpro   = vids["CleanPro Services Pte Ltd"]
    sparkclean = vids["SparkClean International"]
    techfix    = vids["TechFix Engineering Pte Ltd"]
    kone       = vids["Kone Elevator Services"]
    secureguard= vids["SecureGuard Asia Pte Ltd"]
    certis     = vids["Certis CISCO Security"]

    # ── Cleaning Schedules ────────────────────────────────────────────
    cleaning = [
        {"title": "Daily Common Area Cleaning – All Floors",      "assigned_vendor_id": cleanpro,   "frequency": "daily",    "start_date": "2025-01-01", "end_date": "2025-12-31", "status": "in_progress"},
        {"title": "Weekly Deep Clean – Lobby & Lift Lobbies",     "assigned_vendor_id": cleanpro,   "frequency": "weekly",   "start_date": "2025-01-06", "end_date": "2025-12-29", "status": "scheduled"},
        {"title": "Daily Toilet Sanitation – All Levels",         "assigned_vendor_id": sparkclean, "frequency": "daily",    "start_date": "2025-01-01", "end_date": "2025-12-31", "status": "in_progress"},
        {"title": "Biweekly Façade & Window Cleaning",            "assigned_vendor_id": sparkclean, "frequency": "biweekly", "start_date": "2025-02-03", "end_date": "2025-12-31", "status": "scheduled"},
        {"title": "Monthly Carpet Shampooing – Conference Rooms", "assigned_vendor_id": cleanpro,   "frequency": "monthly",  "start_date": "2025-01-15", "end_date": "2025-12-15", "status": "scheduled"},
        {"title": "Weekly Car Park Sweeping",                     "assigned_vendor_id": sparkclean, "frequency": "weekly",   "start_date": "2025-01-06", "end_date": "2025-12-31", "status": "in_progress"},
    ]
    for c in cleaning:
        c["building_id"] = bids
        c["notes"] = "Scheduled as per facility management plan FY2025."
    await db.cleaning_schedules.insert_many(cleaning)
    print(f"Cleaning schedules: {len(cleaning)}")

    # ── Preventive Maintenance ────────────────────────────────────────
    pm_items = [
        {"title": "Quarterly HVAC Filter Replacement",         "category": "hvac",        "frequency": "quarterly", "next_due_date": d(15),  "assigned_vendor_id": techfix, "status": "scheduled", "priority": "medium",   "estimated_cost": 3200.00,  "floor_id": fids[10], "unit_id": uids["L10-ME"]},
        {"title": "Monthly Fire Suppression System Test",      "category": "fire_safety", "frequency": "monthly",   "next_due_date": d(7),   "assigned_vendor_id": techfix, "status": "scheduled", "priority": "high",     "estimated_cost": 1500.00,  "floor_id": None,     "unit_id": None},
        {"title": "Bi-annual Elevator Full Inspection",        "category": "elevator",    "frequency": "biannual",  "next_due_date": d(45),  "assigned_vendor_id": kone,   "status": "scheduled", "priority": "high",     "estimated_cost": 8000.00,  "floor_id": None,     "unit_id": None},
        {"title": "Monthly Elevator Oil & Cable Check",        "category": "elevator",    "frequency": "monthly",   "next_due_date": d(10),  "assigned_vendor_id": kone,   "status": "scheduled", "priority": "medium",   "estimated_cost": 2200.00,  "floor_id": None,     "unit_id": None},
        {"title": "Quarterly Electrical Panel Inspection",     "category": "electrical",  "frequency": "quarterly", "next_due_date": d(-3),  "assigned_vendor_id": techfix, "status": "overdue",   "priority": "high",     "estimated_cost": 4500.00,  "floor_id": fids[10], "unit_id": uids["L10-ME"]},
        {"title": "Monthly Plumbing Leak Check – All Floors",  "category": "plumbing",    "frequency": "monthly",   "next_due_date": d(5),   "assigned_vendor_id": techfix, "status": "scheduled", "priority": "medium",   "estimated_cost": 1200.00,  "floor_id": None,     "unit_id": None},
        {"title": "Annual Structural Façade Inspection",       "category": "structural",  "frequency": "yearly",    "next_due_date": d(90),  "assigned_vendor_id": techfix, "status": "scheduled", "priority": "low",      "estimated_cost": 15000.00, "floor_id": None,     "unit_id": None},
        {"title": "Monthly Emergency Lighting Test",           "category": "electrical",  "frequency": "monthly",   "next_due_date": d(12),  "assigned_vendor_id": techfix, "status": "scheduled", "priority": "medium",   "estimated_cost": 800.00,   "floor_id": None,     "unit_id": None},
        {"title": "Quarterly Chiller Plant Servicing",         "category": "hvac",        "frequency": "quarterly", "next_due_date": d(-7),  "assigned_vendor_id": techfix, "status": "overdue",   "priority": "critical", "estimated_cost": 12000.00, "floor_id": fids[10], "unit_id": uids["L10-ME"]},
        {"title": "Yearly Roof Waterproofing Inspection",      "category": "structural",  "frequency": "yearly",    "next_due_date": d(120), "assigned_vendor_id": techfix, "status": "scheduled", "priority": "medium",   "estimated_cost": 6500.00,  "floor_id": fids[10], "unit_id": uids["L10-RT"]},
    ]
    for p in pm_items:
        p["building_id"] = bids
        p["description"] = f"Routine {p['category'].replace('_',' ')} preventive maintenance per manufacturer schedule."
    await db.preventive_maintenance.insert_many(pm_items)
    print(f"Preventive maintenance: {len(pm_items)}")

    # ── Corrective Maintenance  (with floor_id + unit_id) ─────────────
    cm_items = [
        {
            "title": "Level 5 Air-Con Unit Not Cooling",
            "category": "hvac",         "floor_id": fids[5],  "unit_id": uids["L5-01"],
            "reported_by": "Grab Holdings Facilities", "reported_date": d(-10),
            "assigned_vendor_id": techfix,  "status": "in_progress", "priority": "high",
            "actual_cost": None,  "completion_date": None,  "resolution_notes": None,
        },
        {
            "title": "Ground Floor Toilet – Pipe Burst",
            "category": "plumbing",     "floor_id": fids[1],  "unit_id": uids["G-LBY"],
            "reported_by": "Housekeeping Team",        "reported_date": d(-3),
            "assigned_vendor_id": techfix,  "status": "completed",   "priority": "critical",
            "actual_cost": 3800.00, "completion_date": d(-1),
            "resolution_notes": "Replaced burst pipe section under G-LBY washroom.",
        },
        {
            "title": "Elevator #2 – Door Sensor Fault",
            "category": "elevator",     "floor_id": None,     "unit_id": None,
            "reported_by": "Security Post",            "reported_date": d(-6),
            "assigned_vendor_id": kone,     "status": "completed",   "priority": "high",
            "actual_cost": 2200.00, "completion_date": d(-2),
            "resolution_notes": "Replaced door sensor and recalibrated door alignment.",
        },
        {
            "title": "Level 3 – Office Lighting Flickering",
            "category": "electrical",   "floor_id": fids[3],  "unit_id": uids["L3-01"],
            "reported_by": "Accenture Pte Ltd",        "reported_date": d(-1),
            "assigned_vendor_id": techfix,  "status": "open",        "priority": "medium",
            "actual_cost": None, "completion_date": None, "resolution_notes": None,
        },
        {
            "title": "Car Park – Barrier Gate Motor Failure",
            "category": "general",      "floor_id": fids[1],  "unit_id": uids["G-LBY"],
            "reported_by": "Parking Attendant",        "reported_date": d(-8),
            "assigned_vendor_id": techfix,  "status": "in_progress", "priority": "high",
            "actual_cost": None, "completion_date": None, "resolution_notes": None,
        },
        {
            "title": "Level 9 Events Hall – AV System Down",
            "category": "electrical",   "floor_id": fids[9],  "unit_id": uids["L9-EVT"],
            "reported_by": "Events Coordinator",       "reported_date": d(-2),
            "assigned_vendor_id": techfix,  "status": "open",        "priority": "medium",
            "actual_cost": None, "completion_date": None, "resolution_notes": None,
        },
        {
            "title": "Level 2 Starbucks – Exhaust Fan Noisy",
            "category": "hvac",         "floor_id": fids[2],  "unit_id": uids["L2-02"],
            "reported_by": "Starbucks Manager",        "reported_date": d(-14),
            "assigned_vendor_id": techfix,  "status": "closed",      "priority": "low",
            "actual_cost": 450.00, "completion_date": d(-9),
            "resolution_notes": "Tightened fan belt and lubricated bearings.",
        },
        {
            "title": "Fire Alarm False Trigger – Level 6",
            "category": "fire_safety",  "floor_id": fids[6],  "unit_id": uids["L6-SR"],
            "reported_by": "Security Post",            "reported_date": d(-4),
            "assigned_vendor_id": techfix,  "status": "completed",   "priority": "critical",
            "actual_cost": 1800.00, "completion_date": d(-2),
            "resolution_notes": "Replaced faulty smoke detector unit in server room area.",
        },
        {
            "title": "Level 4 – Water Seepage from Ceiling",
            "category": "plumbing",     "floor_id": fids[4],  "unit_id": uids["L4-01"],
            "reported_by": "Siemens Facilities Mgr",   "reported_date": d(-5),
            "assigned_vendor_id": techfix,  "status": "in_progress", "priority": "high",
            "actual_cost": None, "completion_date": None, "resolution_notes": None,
        },
        {
            "title": "Level 8 – Power Socket Short Circuit",
            "category": "electrical",   "floor_id": fids[8],  "unit_id": uids["L8-01"],
            "reported_by": "EY Singapore IT Dept",     "reported_date": d(-2),
            "assigned_vendor_id": techfix,  "status": "open",        "priority": "high",
            "actual_cost": None, "completion_date": None, "resolution_notes": None,
        },
    ]
    for c in cm_items:
        c["building_id"] = bids
        c["description"] = c["title"] + " – requires immediate attention by facility management."
    await db.corrective_maintenance.insert_many(cm_items)
    print(f"Corrective maintenance: {len(cm_items)}")

    # ── Cases (with floor_id + unit_id) ───────────────────────────────
    cases_raw = [
        {"title": "Parking Lot – Unauthorized Vehicle",        "category": "complaint",  "floor_id": fids[1],  "unit_id": uids["G-LBY"], "reported_by": "DBS Bank Facilities Mgr", "contact_phone": "+65 6123 4004", "status": "open",        "priority": "medium",   "assigned_to": "Security Team"},
        {"title": "Lobby Temperature Too Cold",                "category": "complaint",  "floor_id": fids[1],  "unit_id": uids["G-LBY"], "reported_by": "Grab Holdings Staff",      "contact_phone": "+65 6345 6001", "status": "in_progress", "priority": "low",      "assigned_to": "Building Operations"},
        {"title": "Suspicious Person Near Server Room L3",     "category": "emergency",  "floor_id": fids[3],  "unit_id": uids["L3-SR"], "reported_by": "Security Post Alpha",      "contact_phone": "+65 9100 9001", "status": "resolved",    "priority": "critical", "assigned_to": "Security Team",       "resolution_notes": "Visitor escorted out. Access badge audit completed."},
        {"title": "Request for Additional Parking Lot Access", "category": "request",    "floor_id": fids[1],  "unit_id": uids["G-LBY"], "reported_by": "Accenture HR",             "contact_phone": "+65 6234 5001", "status": "open",        "priority": "low",      "assigned_to": "Admin Office"},
        {"title": "Water Leakage from L4 Ceiling",             "category": "emergency",  "floor_id": fids[4],  "unit_id": uids["L4-01"], "reported_by": "HP Inc Facilities",        "contact_phone": "+65 6234 5004", "status": "in_progress", "priority": "critical", "assigned_to": "Maintenance Team"},
        {"title": "Inquiry: Meeting Room Booking Procedure",   "category": "inquiry",    "floor_id": fids[5],  "unit_id": uids["L5-MR"], "reported_by": "Shopee New Staff",         "contact_phone": "+65 6345 6003", "status": "closed",      "priority": "low",      "assigned_to": "Reception",           "resolution_notes": "Emailed booking portal guide and SOP to tenant."},
        {"title": "Lift #3 Making Grinding Noise",             "category": "complaint",  "floor_id": None,     "unit_id": None,          "reported_by": "Toast Box Manager",        "contact_phone": "+65 6123 4002", "status": "open",        "priority": "high",     "assigned_to": "Maintenance Team"},
        {"title": "Broken Lock – Level 9 Conference Room B",   "category": "request",    "floor_id": fids[9],  "unit_id": uids["L9-CR2"],"reported_by": "Events Coordinator",       "contact_phone": "+65 9200 0001", "status": "resolved",    "priority": "medium",   "assigned_to": "Maintenance Team",    "resolution_notes": "Lock mechanism replaced with new electronic keypad."},
        {"title": "Food Smell Spreading from L2 Food Court",   "category": "complaint",  "floor_id": fids[2],  "unit_id": uids["L2-01"], "reported_by": "Bosch Singapore HR",       "contact_phone": "+65 6234 5002", "status": "in_progress", "priority": "medium",   "assigned_to": "Building Operations"},
        {"title": "Power Trip in Unit L3-04",                  "category": "emergency",  "floor_id": fids[3],  "unit_id": uids["L3-04"], "reported_by": "HP Inc IT Manager",        "contact_phone": "+65 6234 5004", "status": "resolved",    "priority": "critical", "assigned_to": "Maintenance Team",    "resolution_notes": "Identified overloaded circuit breaker, load redistributed."},
        {"title": "L6 Server Room – Cooling Unit Alarm",       "category": "emergency",  "floor_id": fids[6],  "unit_id": uids["L6-SR"], "reported_by": "Google Singapore IT",      "contact_phone": "+65 6789 1001", "status": "in_progress", "priority": "critical", "assigned_to": "Maintenance Team"},
        {"title": "Washroom Out of Order – Level 7",           "category": "complaint",  "floor_id": fids[7],  "unit_id": uids["L7-WC"], "reported_by": "Deloitte Office Mgr",      "contact_phone": "+65 6224 8288", "status": "open",        "priority": "medium",   "assigned_to": "Housekeeping"},
    ]
    for i, c in enumerate(cases_raw):
        c["building_id"] = bids
        c.setdefault("resolution_notes", None)
        c["description"] = c["title"] + " – reported by tenant, requires facility management action."
        created = datetime.now(timezone.utc) - timedelta(days=len(cases_raw) - i)
        c["created_at"] = created.isoformat()
        c["updated_at"] = created.isoformat()
        prefix = f"CASE-{datetime.now(timezone.utc).strftime('%Y%m')}-"
        count = await db.cases.count_documents({"case_number": {"$regex": f"^{prefix}"}})
        c["case_number"] = f"{prefix}{str(count + 1).zfill(4)}"
        await db.cases.insert_one(c)
    print(f"Cases: {len(cases_raw)}")

    # ── Costs ─────────────────────────────────────────────────────────
    costs_data = [
        {"category": "cleaning",    "description": "CleanPro – Jan 2025 Monthly Invoice",          "amount": 12800.00, "date": "2025-01-31", "vendor_id": cleanpro,    "reference_no": "INV-CP-2501",  "status": "paid",    "payment_method": "bank_transfer"},
        {"category": "cleaning",    "description": "SparkClean – Jan 2025 Supplementary Cleaning", "amount":  4500.00, "date": "2025-01-31", "vendor_id": sparkclean,  "reference_no": "INV-SC-2501",  "status": "paid",    "payment_method": "bank_transfer"},
        {"category": "maintenance", "description": "TechFix – HVAC Quarterly Servicing Q1",        "amount":  9600.00, "date": "2025-02-10", "vendor_id": techfix,     "reference_no": "INV-TF-2502",  "status": "paid",    "payment_method": "bank_transfer"},
        {"category": "maintenance", "description": "Kone Elevator – Monthly Maintenance Jan",      "amount":  6800.00, "date": "2025-01-15", "vendor_id": kone,        "reference_no": "INV-KN-2501",  "status": "paid",    "payment_method": "cheque"},
        {"category": "security",    "description": "SecureGuard – Jan 2025 Security Services",     "amount": 18500.00, "date": "2025-01-31", "vendor_id": secureguard, "reference_no": "INV-SG-2501",  "status": "paid",    "payment_method": "bank_transfer"},
        {"category": "security",    "description": "Certis CISCO – Jan 2025 CCTV Monitoring",      "amount":  5200.00, "date": "2025-01-31", "vendor_id": certis,      "reference_no": "INV-CC-2501",  "status": "paid",    "payment_method": "bank_transfer"},
        {"category": "utilities",   "description": "SP Group – Electricity Jan 2025",               "amount": 42500.00, "date": "2025-02-05", "vendor_id": None,        "reference_no": "SP-0125",      "status": "paid",    "payment_method": "online"},
        {"category": "utilities",   "description": "PUB – Water & Sewerage Jan 2025",               "amount":  8200.00, "date": "2025-02-05", "vendor_id": None,        "reference_no": "PUB-0125",     "status": "paid",    "payment_method": "online"},
        {"category": "cleaning",    "description": "CleanPro – Feb 2025 Monthly Invoice",          "amount": 12800.00, "date": "2025-02-28", "vendor_id": cleanpro,    "reference_no": "INV-CP-2502",  "status": "paid",    "payment_method": "bank_transfer"},
        {"category": "maintenance", "description": "TechFix – Corrective: Pipe Burst Repair",      "amount":  3800.00, "date": "2025-03-02", "vendor_id": techfix,     "reference_no": "INV-TF-2503A", "status": "paid",    "payment_method": "bank_transfer"},
        {"category": "maintenance", "description": "Kone Elevator – Door Sensor Replacement",      "amount":  2200.00, "date": "2025-03-05", "vendor_id": kone,        "reference_no": "INV-KN-2503",  "status": "paid",    "payment_method": "cheque"},
        {"category": "maintenance", "description": "TechFix – Fire Alarm Sensor Replacement L6",   "amount":  1800.00, "date": "2025-03-08", "vendor_id": techfix,     "reference_no": "INV-TF-2503B", "status": "paid",    "payment_method": "bank_transfer"},
        {"category": "security",    "description": "SecureGuard – Feb 2025 Security Services",     "amount": 18500.00, "date": "2025-02-28", "vendor_id": secureguard, "reference_no": "INV-SG-2502",  "status": "paid",    "payment_method": "bank_transfer"},
        {"category": "utilities",   "description": "SP Group – Electricity Feb 2025",               "amount": 39800.00, "date": "2025-03-05", "vendor_id": None,        "reference_no": "SP-0225",      "status": "paid",    "payment_method": "online"},
        {"category": "cleaning",    "description": "SparkClean – Mar 2025 Façade Cleaning",        "amount":  6500.00, "date": d(-5),        "vendor_id": sparkclean,  "reference_no": "INV-SC-2503",  "status": "pending", "payment_method": "bank_transfer"},
        {"category": "maintenance", "description": "TechFix – Chiller Plant Emergency Service",    "amount": 12000.00, "date": d(-2),        "vendor_id": techfix,     "reference_no": "INV-TF-2503C", "status": "pending", "payment_method": None},
        {"category": "utilities",   "description": "SP Group – Electricity Mar 2025",               "amount": 41200.00, "date": d(5),         "vendor_id": None,        "reference_no": "SP-0325",      "status": "pending", "payment_method": None},
        {"category": "others",      "description": "BizSafe Audit & Certification Renewal",        "amount":  3500.00, "date": d(10),        "vendor_id": None,        "reference_no": "BCA-2025",     "status": "pending", "payment_method": None},
    ]
    for c in costs_data:
        c["building_id"] = bids
    await db.costs.insert_many(costs_data)
    print(f"Costs: {len(costs_data)}")

    # ── Night Watch Duty Roster ───────────────────────────────────────
    roster_data = [
        {"date": d(-6), "shift": "night",   "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "completed", "notes": "Regular patrol – no incidents."},
        {"date": d(-5), "shift": "night",   "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "completed", "notes": "Minor loitering at G floor, resolved."},
        {"date": d(-4), "shift": "night",   "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "completed", "notes": "Regular patrol – all clear."},
        {"date": d(-3), "shift": "night",   "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "completed", "notes": "Suspicious individual reported, escorted off premises."},
        {"date": d(-2), "shift": "night",   "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "completed", "notes": "Regular patrol – all clear."},
        {"date": d(-1), "shift": "night",   "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "completed", "notes": "Regular patrol – all clear."},
        {"date": d(0),  "shift": "night",   "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "scheduled", "notes": "Patrol + CCTV monitoring."},
        {"date": d(1),  "shift": "night",   "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "scheduled", "notes": None},
        {"date": d(2),  "shift": "night",   "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "scheduled", "notes": None},
        {"date": d(3),  "shift": "night",   "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "scheduled", "notes": None},
        {"date": d(4),  "shift": "night",   "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "scheduled", "notes": None},
        {"date": d(5),  "shift": "night",   "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "scheduled", "notes": None},
        {"date": d(6),  "shift": "night",   "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "scheduled", "notes": None},
        {"date": d(0),  "shift": "morning", "start_time": "06:00", "end_time": "14:00", "assigned_officer_ids": [], "status": "scheduled", "notes": "Morning access control + patrol."},
        {"date": d(1),  "shift": "morning", "start_time": "06:00", "end_time": "14:00", "assigned_officer_ids": [], "status": "scheduled", "notes": None},
        {"date": d(2),  "shift": "morning", "start_time": "06:00", "end_time": "14:00", "assigned_officer_ids": [], "status": "scheduled", "notes": None},
    ]
    for r in roster_data:
        r["building_id"] = bids
    await db.roster.insert_many(roster_data)
    print(f"Roster: {len(roster_data)}")

    # ── Attendance ────────────────────────────────────────────────────
    attendance_data = []
    for offset in range(-13, 1):
        dt = d(offset)
        if (TODAY + timedelta(days=offset)).weekday() >= 5:
            continue
        attendance_data += [
            {"attendance_type": "cleaner",  "person_id": cleanpro,    "building_id": bids, "date": dt, "check_in_time": "07:00", "check_out_time": "15:00", "status": "present", "notes": None},
            {"attendance_type": "cleaner",  "person_id": sparkclean,  "building_id": bids, "date": dt, "check_in_time": "08:00" if offset != -3 else None,  "check_out_time": "16:00" if offset != -3 else None, "status": "present" if offset != -3 else "absent", "notes": "No show" if offset == -3 else None},
            {"attendance_type": "security", "person_id": secureguard, "building_id": bids, "date": dt, "check_in_time": "08:00", "check_out_time": "20:00", "status": "present", "notes": None},
            {"attendance_type": "security", "person_id": certis,      "building_id": bids, "date": dt, "check_in_time": "08:30" if offset != -5 else "09:15","check_out_time": "20:00", "status": "present" if offset != -5 else "late", "notes": "Late arrival" if offset == -5 else None},
        ]
    await db.attendance.insert_many(attendance_data)
    print(f"Attendance: {len(attendance_data)}")

    print("\n✅  Seed complete! Mappletree Business City loaded into resolveapp DB.")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
