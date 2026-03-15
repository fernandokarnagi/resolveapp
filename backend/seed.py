"""
Seed script: Mappletree Business City, Singapore sample data.
Run: source venv/bin/activate && python seed.py
"""
import asyncio
from datetime import date, timedelta
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
    building_doc = {
        "name": "Mappletree Business City",
        "address": "20 Pasir Panjang Road, Singapore 117439",
        "total_floors": 10,
        "status": "active",
        "description": "Grade-A business park campus by Mapletree Investments, "
                       "comprising office, retail, and ancillary facilities.",
    }
    res = await db.buildings.insert_one(building_doc)
    bid = res.inserted_id
    bids = str(bid)
    print(f"Building inserted: {bids}")

    # ── Floors ────────────────────────────────────────────────────────
    floors_data = [
        {"floor_number": 1, "name": "Ground Floor – Retail & Lobby", "total_units": 8},
        {"floor_number": 2, "name": "Level 2 – F&B & Amenities",     "total_units": 6},
        {"floor_number": 3, "name": "Level 3 – Office",              "total_units": 12},
        {"floor_number": 4, "name": "Level 4 – Office",              "total_units": 12},
        {"floor_number": 5, "name": "Level 5 – Office",              "total_units": 10},
        {"floor_number": 6, "name": "Level 6 – Office",              "total_units": 10},
        {"floor_number": 7, "name": "Level 7 – Office",              "total_units": 8},
        {"floor_number": 8, "name": "Level 8 – Office",              "total_units": 8},
        {"floor_number": 9, "name": "Level 9 – Conference & Events", "total_units": 5},
        {"floor_number": 10,"name": "Level 10 – Rooftop & M&E",     "total_units": 3},
    ]
    floor_ids = {}
    for f in floors_data:
        f["building_id"] = bids
        res = await db.floors.insert_one(f)
        floor_ids[f["floor_number"]] = str(res.inserted_id)
    print(f"Floors inserted: {len(floor_ids)}")

    # ── Units ─────────────────────────────────────────────────────────
    units = [
        # Ground floor – retail
        {"unit_number": "G-01", "floor_number": 1, "type": "commercial", "status": "occupied",  "area_sqft": 2500, "tenant_name": "Guardian Pharmacy",       "tenant_contact": "+65 6123 4001"},
        {"unit_number": "G-02", "floor_number": 1, "type": "commercial", "status": "occupied",  "area_sqft": 1800, "tenant_name": "Toast Box Café",          "tenant_contact": "+65 6123 4002"},
        {"unit_number": "G-03", "floor_number": 1, "type": "commercial", "status": "vacant",    "area_sqft": 1500, "tenant_name": None,                      "tenant_contact": None},
        {"unit_number": "G-04", "floor_number": 1, "type": "commercial", "status": "occupied",  "area_sqft": 3200, "tenant_name": "DBS Bank Branch",         "tenant_contact": "+65 6123 4004"},
        {"unit_number": "G-LBY","floor_number": 1, "type": "common",     "status": "occupied",  "area_sqft": 4500, "tenant_name": "Main Lobby",              "tenant_contact": None},
        # Level 2 – F&B
        {"unit_number": "L2-01","floor_number": 2, "type": "commercial", "status": "occupied",  "area_sqft": 3000, "tenant_name": "Koufu Food Court",        "tenant_contact": "+65 6123 4201"},
        {"unit_number": "L2-02","floor_number": 2, "type": "commercial", "status": "occupied",  "area_sqft": 1200, "tenant_name": "Starbucks",               "tenant_contact": "+65 6123 4202"},
        {"unit_number": "L2-03","floor_number": 2, "type": "commercial", "status": "vacant",    "area_sqft": 2000, "tenant_name": None,                      "tenant_contact": None},
        # Level 3 – Office
        {"unit_number": "L3-01","floor_number": 3, "type": "residential","status": "occupied",  "area_sqft": 5000, "tenant_name": "Accenture Pte Ltd",       "tenant_contact": "+65 6234 5001"},
        {"unit_number": "L3-02","floor_number": 3, "type": "residential","status": "occupied",  "area_sqft": 4800, "tenant_name": "Bosch Singapore",         "tenant_contact": "+65 6234 5002"},
        {"unit_number": "L3-03","floor_number": 3, "type": "residential","status": "vacant",    "area_sqft": 4500, "tenant_name": None,                      "tenant_contact": None},
        {"unit_number": "L3-04","floor_number": 3, "type": "residential","status": "occupied",  "area_sqft": 6000, "tenant_name": "HP Inc Singapore",        "tenant_contact": "+65 6234 5004"},
        # Level 5 – Office
        {"unit_number": "L5-01","floor_number": 5, "type": "residential","status": "occupied",  "area_sqft": 7200, "tenant_name": "Grab Holdings",           "tenant_contact": "+65 6345 6001"},
        {"unit_number": "L5-02","floor_number": 5, "type": "residential","status": "maintenance","area_sqft":3500, "tenant_name": None,                      "tenant_contact": None},
        {"unit_number": "L5-03","floor_number": 5, "type": "residential","status": "occupied",  "area_sqft": 4000, "tenant_name": "Shopee (SEA Ltd)",        "tenant_contact": "+65 6345 6003"},
        # Level 9 – Conference
        {"unit_number": "L9-CR1","floor_number":9, "type": "common",     "status": "occupied",  "area_sqft": 1800, "tenant_name": "Conference Room A",       "tenant_contact": None},
        {"unit_number": "L9-CR2","floor_number":9, "type": "common",     "status": "occupied",  "area_sqft": 1200, "tenant_name": "Conference Room B",       "tenant_contact": None},
        {"unit_number": "L9-EVT","floor_number":9, "type": "common",     "status": "occupied",  "area_sqft": 5000, "tenant_name": "Events Hall",             "tenant_contact": None},
        # Level 10 – M&E
        {"unit_number": "L10-ME","floor_number":10,"type": "common",     "status": "maintenance","area_sqft":2000, "tenant_name": "M&E Plant Room",          "tenant_contact": None},
    ]
    for u in units:
        fn = u.pop("floor_number")
        u["floor_id"] = floor_ids[fn]
        u["building_id"] = bids
        await db.units.insert_one(u)
    print(f"Units inserted: {len(units)}")

    # ── Vendors ───────────────────────────────────────────────────────
    vendors_data = [
        {
            "name": "CleanPro Services Pte Ltd",
            "type": "cleaning",
            "contact_person": "Tan Wei Ming",
            "phone": "+65 8100 2001",
            "email": "ops@cleanpro.sg",
            "address": "18 Tuas Ave 5, Singapore 639340",
            "status": "active",
            "contract_start": "2024-01-01",
            "contract_end": "2026-12-31",
            "hourly_rate": 18.50,
        },
        {
            "name": "SparkClean International",
            "type": "cleaning",
            "contact_person": "Lim Hui Ling",
            "phone": "+65 8200 3002",
            "email": "hello@sparkclean.sg",
            "address": "30 Jalan Buroh, Singapore 619493",
            "status": "active",
            "contract_start": "2024-06-01",
            "contract_end": "2025-12-31",
            "hourly_rate": 16.00,
        },
        {
            "name": "TechFix Engineering Pte Ltd",
            "type": "maintenance",
            "contact_person": "Rajesh Kumar",
            "phone": "+65 9100 4001",
            "email": "service@techfix.sg",
            "address": "12 Woodlands Link, Singapore 738733",
            "status": "active",
            "contract_start": "2023-07-01",
            "contract_end": "2026-06-30",
            "hourly_rate": 65.00,
        },
        {
            "name": "Kone Elevator Services",
            "type": "maintenance",
            "contact_person": "David Ng",
            "phone": "+65 6300 5000",
            "email": "sg.support@kone.com",
            "address": "2 Kallang Ave, #07-18, Singapore 339407",
            "status": "active",
            "contract_start": "2022-01-01",
            "contract_end": "2027-12-31",
            "hourly_rate": 120.00,
        },
        {
            "name": "SecureGuard Asia Pte Ltd",
            "type": "security",
            "contact_person": "Mohammad Farid",
            "phone": "+65 8300 6001",
            "email": "ops@secureguard.sg",
            "address": "8 Admiralty St, Singapore 757438",
            "status": "active",
            "contract_start": "2024-01-01",
            "contract_end": "2025-12-31",
            "hourly_rate": 22.00,
        },
        {
            "name": "Certis CISCO Security",
            "type": "security",
            "contact_person": "Ng Boon Kiat",
            "phone": "+65 6888 7000",
            "email": "info@certiscisco.com.sg",
            "address": "1 Certis CISCO Centre, Singapore 488922",
            "status": "active",
            "contract_start": "2023-01-01",
            "contract_end": "2026-12-31",
            "hourly_rate": 25.00,
        },
    ]
    vendor_ids = {}
    for v in vendors_data:
        res = await db.vendors.insert_one(v)
        vendor_ids[v["name"]] = str(res.inserted_id)
    print(f"Vendors inserted: {len(vendor_ids)}")

    cleanpro = vendor_ids["CleanPro Services Pte Ltd"]
    sparkclean = vendor_ids["SparkClean International"]
    techfix = vendor_ids["TechFix Engineering Pte Ltd"]
    kone = vendor_ids["Kone Elevator Services"]
    secureguard = vendor_ids["SecureGuard Asia Pte Ltd"]
    certis = vendor_ids["Certis CISCO Security"]

    # ── Cleaning Schedules ────────────────────────────────────────────
    cleaning = [
        {"title": "Daily Common Area Cleaning – All Floors",     "assigned_vendor_id": cleanpro,   "frequency": "daily",    "start_date": "2025-01-01", "end_date": "2025-12-31", "status": "in_progress"},
        {"title": "Weekly Deep Clean – Lobby & Lift Lobbies",    "assigned_vendor_id": cleanpro,   "frequency": "weekly",   "start_date": "2025-01-06", "end_date": "2025-12-29", "status": "scheduled"},
        {"title": "Daily Toilet Sanitation – All Levels",        "assigned_vendor_id": sparkclean, "frequency": "daily",    "start_date": "2025-01-01", "end_date": "2025-12-31", "status": "in_progress"},
        {"title": "Biweekly Façade & Window Cleaning",           "assigned_vendor_id": sparkclean, "frequency": "biweekly", "start_date": "2025-02-03", "end_date": "2025-12-31", "status": "scheduled"},
        {"title": "Monthly Carpet Shampooing – Conference Rooms","assigned_vendor_id": cleanpro,   "frequency": "monthly",  "start_date": "2025-01-15", "end_date": "2025-12-15", "status": "scheduled"},
        {"title": "Weekly Car Park Sweeping",                    "assigned_vendor_id": sparkclean, "frequency": "weekly",   "start_date": "2025-01-06", "end_date": "2025-12-31", "status": "in_progress"},
    ]
    for c in cleaning:
        c["building_id"] = bids
        c["notes"] = "Scheduled as per facility management plan FY2025."
    await db.cleaning_schedules.insert_many(cleaning)
    print(f"Cleaning schedules inserted: {len(cleaning)}")

    # ── Preventive Maintenance ────────────────────────────────────────
    pm_items = [
        {"title": "Quarterly HVAC Filter Replacement",          "category": "hvac",        "frequency": "quarterly", "next_due_date": d(15),  "assigned_vendor_id": techfix,  "status": "scheduled",  "priority": "medium",   "estimated_cost": 3200.00},
        {"title": "Monthly Fire Suppression System Test",       "category": "fire_safety", "frequency": "monthly",   "next_due_date": d(7),   "assigned_vendor_id": techfix,  "status": "scheduled",  "priority": "high",     "estimated_cost": 1500.00},
        {"title": "Bi-annual Elevator Full Inspection",         "category": "elevator",    "frequency": "biannual",  "next_due_date": d(45),  "assigned_vendor_id": kone,     "status": "scheduled",  "priority": "high",     "estimated_cost": 8000.00},
        {"title": "Monthly Elevator Oil & Cable Check",         "category": "elevator",    "frequency": "monthly",   "next_due_date": d(10),  "assigned_vendor_id": kone,     "status": "scheduled",  "priority": "medium",   "estimated_cost": 2200.00},
        {"title": "Quarterly Electrical Panel Inspection",      "category": "electrical",  "frequency": "quarterly", "next_due_date": d(-3),  "assigned_vendor_id": techfix,  "status": "overdue",    "priority": "high",     "estimated_cost": 4500.00},
        {"title": "Monthly Plumbing Leak Check – All Floors",   "category": "plumbing",    "frequency": "monthly",   "next_due_date": d(5),   "assigned_vendor_id": techfix,  "status": "scheduled",  "priority": "medium",   "estimated_cost": 1200.00},
        {"title": "Annual Structural Façade Inspection",        "category": "structural",  "frequency": "yearly",    "next_due_date": d(90),  "assigned_vendor_id": techfix,  "status": "scheduled",  "priority": "low",      "estimated_cost": 15000.00},
        {"title": "Monthly Emergency Lighting Test",            "category": "electrical",  "frequency": "monthly",   "next_due_date": d(12),  "assigned_vendor_id": techfix,  "status": "scheduled",  "priority": "medium",   "estimated_cost": 800.00},
        {"title": "Quarterly Chiller Plant Servicing",          "category": "hvac",        "frequency": "quarterly", "next_due_date": d(-7),  "assigned_vendor_id": techfix,  "status": "overdue",    "priority": "critical", "estimated_cost": 12000.00},
        {"title": "Yearly Roof Waterproofing Inspection",       "category": "structural",  "frequency": "yearly",    "next_due_date": d(120), "assigned_vendor_id": techfix,  "status": "scheduled",  "priority": "medium",   "estimated_cost": 6500.00},
    ]
    for p in pm_items:
        p["building_id"] = bids
        p["description"] = f"Routine {p['category'].replace('_',' ')} preventive maintenance per manufacturer schedule."
    await db.preventive_maintenance.insert_many(pm_items)
    print(f"Preventive maintenance inserted: {len(pm_items)}")

    # ── Corrective Maintenance ────────────────────────────────────────
    cm_items = [
        {"title": "Level 5 Air-Con Unit Not Cooling",        "category": "hvac",        "reported_by": "Grab Holdings Facilities", "reported_date": d(-10), "assigned_vendor_id": techfix,  "status": "in_progress", "priority": "high",     "actual_cost": None,      "completion_date": None,  "resolution_notes": None},
        {"title": "Ground Floor Toilet – Pipe Burst",        "category": "plumbing",    "reported_by": "Housekeeping Team",       "reported_date": d(-3),  "assigned_vendor_id": techfix,  "status": "completed",   "priority": "critical", "actual_cost": 3800.00,  "completion_date": d(-1), "resolution_notes": "Replaced burst pipe section under G-LBY washroom."},
        {"title": "Elevator #2 – Door Sensor Fault",         "category": "elevator",    "reported_by": "Security Post",           "reported_date": d(-6),  "assigned_vendor_id": kone,     "status": "completed",   "priority": "high",     "actual_cost": 2200.00,  "completion_date": d(-2), "resolution_notes": "Replaced door sensor and recalibrated door alignment."},
        {"title": "Level 3 – Office Lighting Flickering",    "category": "electrical",  "reported_by": "Accenture Pte Ltd",       "reported_date": d(-1),  "assigned_vendor_id": techfix,  "status": "open",        "priority": "medium",   "actual_cost": None,      "completion_date": None,  "resolution_notes": None},
        {"title": "Car Park – Barrier Gate Motor Failure",   "category": "general",     "reported_by": "Parking Attendant",       "reported_date": d(-8),  "assigned_vendor_id": techfix,  "status": "in_progress", "priority": "high",     "actual_cost": None,      "completion_date": None,  "resolution_notes": None},
        {"title": "Level 9 Events Hall – AV System Down",    "category": "electrical",  "reported_by": "Events Coordinator",      "reported_date": d(-2),  "assigned_vendor_id": techfix,  "status": "open",        "priority": "medium",   "actual_cost": None,      "completion_date": None,  "resolution_notes": None},
        {"title": "Level 2 Starbucks – Exhaust Fan Noisy",   "category": "hvac",        "reported_by": "Starbucks Manager",       "reported_date": d(-14), "assigned_vendor_id": techfix,  "status": "closed",      "priority": "low",      "actual_cost": 450.00,   "completion_date": d(-9), "resolution_notes": "Tightened fan belt and lubricated bearings."},
        {"title": "Fire Alarm False Trigger – Level 6",      "category": "fire_safety", "reported_by": "Security Post",           "reported_date": d(-4),  "assigned_vendor_id": techfix,  "status": "completed",   "priority": "critical", "actual_cost": 1800.00,  "completion_date": d(-2), "resolution_notes": "Replaced faulty smoke detector unit in server room area."},
    ]
    for c in cm_items:
        c["building_id"] = bids
        c["description"] = c["title"] + " – requires immediate attention by facility management."
    await db.corrective_maintenance.insert_many(cm_items)
    print(f"Corrective maintenance inserted: {len(cm_items)}")

    # ── Cases ─────────────────────────────────────────────────────────
    cases_data = [
        {"title": "Parking Lot – Unauthorized Vehicle",         "category": "complaint",  "reported_by": "DBS Bank Facilities Mgr",  "contact_phone": "+65 6123 4004", "status": "open",        "priority": "medium",   "assigned_to": "Security Team",       "resolution_notes": None},
        {"title": "Lobby Temperature Too Cold",                 "category": "complaint",  "reported_by": "Grab Holdings Staff",       "contact_phone": "+65 6345 6001", "status": "in_progress", "priority": "low",      "assigned_to": "Building Operations", "resolution_notes": None},
        {"title": "Suspicious Person Near Server Room L3",      "category": "emergency",  "reported_by": "Security Post Alpha",       "contact_phone": "+65 9100 9001", "status": "resolved",    "priority": "critical", "assigned_to": "Security Team",       "resolution_notes": "Visitor escorted out. Access badge audit completed."},
        {"title": "Request for Additional Parking Lot Access",  "category": "request",    "reported_by": "Accenture HR",              "contact_phone": "+65 6234 5001", "status": "open",        "priority": "low",      "assigned_to": "Admin Office",        "resolution_notes": None},
        {"title": "Water Leakage from L4 Ceiling",              "category": "emergency",  "reported_by": "HP Inc Facilities",         "contact_phone": "+65 6234 5004", "status": "in_progress", "priority": "critical", "assigned_to": "Maintenance Team",    "resolution_notes": None},
        {"title": "Inquiry: Meeting Room Booking Procedure",    "category": "inquiry",    "reported_by": "Shopee New Staff",          "contact_phone": "+65 6345 6003", "status": "closed",      "priority": "low",      "assigned_to": "Reception",           "resolution_notes": "Emailed booking portal guide and SOP to tenant."},
        {"title": "Lift #3 Making Grinding Noise",              "category": "complaint",  "reported_by": "Toast Box Manager",         "contact_phone": "+65 6123 4002", "status": "open",        "priority": "high",     "assigned_to": "Maintenance Team",    "resolution_notes": None},
        {"title": "Broken Lock – Level 9 Conference Room B",    "category": "request",    "reported_by": "Events Coordinator",        "contact_phone": "+65 9200 0001", "status": "resolved",    "priority": "medium",   "assigned_to": "Maintenance Team",    "resolution_notes": "Lock mechanism replaced with new electronic keypad."},
        {"title": "Food Smell Spreading from L2 Food Court",    "category": "complaint",  "reported_by": "Bosch Singapore HR",        "contact_phone": "+65 6234 5002", "status": "in_progress", "priority": "medium",   "assigned_to": "Building Operations", "resolution_notes": None},
        {"title": "Power Trip in Unit L3-04",                   "category": "emergency",  "reported_by": "HP Inc IT Manager",         "contact_phone": "+65 6234 5004", "status": "resolved",    "priority": "critical", "assigned_to": "Maintenance Team",    "resolution_notes": "Identified overloaded circuit breaker, load redistributed."},
    ]
    from datetime import datetime, timezone
    for i, c in enumerate(cases_data):
        c["building_id"] = bids
        c["description"] = c["title"] + " – reported by tenant, requires facility management action."
        created = datetime.now(timezone.utc) - timedelta(days=len(cases_data) - i)
        c["created_at"] = created.isoformat()
        c["updated_at"] = created.isoformat()
        now = datetime.now(timezone.utc)
        prefix = f"CASE-{now.strftime('%Y%m')}-"
        count = await db.cases.count_documents({"case_number": {"$regex": f"^{prefix}"}})
        c["case_number"] = f"{prefix}{str(count + 1).zfill(4)}"
        await db.cases.insert_one(c)
    print(f"Cases inserted: {len(cases_data)}")

    # ── Costs ─────────────────────────────────────────────────────────
    costs_data = [
        {"category": "cleaning",     "description": "CleanPro – Jan 2025 Monthly Invoice",           "amount": 12800.00, "date": "2025-01-31", "vendor_id": cleanpro,    "reference_no": "INV-CP-2501", "status": "paid",    "payment_method": "bank_transfer"},
        {"category": "cleaning",     "description": "SparkClean – Jan 2025 Supplementary Cleaning",  "amount":  4500.00, "date": "2025-01-31", "vendor_id": sparkclean,  "reference_no": "INV-SC-2501", "status": "paid",    "payment_method": "bank_transfer"},
        {"category": "maintenance",  "description": "TechFix – HVAC Quarterly Servicing Q1",         "amount":  9600.00, "date": "2025-02-10", "vendor_id": techfix,     "reference_no": "INV-TF-2502", "status": "paid",    "payment_method": "bank_transfer"},
        {"category": "maintenance",  "description": "Kone Elevator – Monthly Maintenance Jan",       "amount":  6800.00, "date": "2025-01-15", "vendor_id": kone,        "reference_no": "INV-KN-2501", "status": "paid",    "payment_method": "cheque"},
        {"category": "security",     "description": "SecureGuard – Jan 2025 Security Services",      "amount": 18500.00, "date": "2025-01-31", "vendor_id": secureguard, "reference_no": "INV-SG-2501", "status": "paid",    "payment_method": "bank_transfer"},
        {"category": "security",     "description": "Certis CISCO – Jan 2025 CCTV Monitoring",       "amount":  5200.00, "date": "2025-01-31", "vendor_id": certis,      "reference_no": "INV-CC-2501", "status": "paid",    "payment_method": "bank_transfer"},
        {"category": "utilities",    "description": "SP Group – Electricity Jan 2025",                "amount": 42500.00, "date": "2025-02-05", "vendor_id": None,        "reference_no": "SP-0125",     "status": "paid",    "payment_method": "online"},
        {"category": "utilities",    "description": "PUB – Water & Sewerage Jan 2025",                "amount":  8200.00, "date": "2025-02-05", "vendor_id": None,        "reference_no": "PUB-0125",    "status": "paid",    "payment_method": "online"},
        {"category": "cleaning",     "description": "CleanPro – Feb 2025 Monthly Invoice",           "amount": 12800.00, "date": "2025-02-28", "vendor_id": cleanpro,    "reference_no": "INV-CP-2502", "status": "paid",    "payment_method": "bank_transfer"},
        {"category": "maintenance",  "description": "TechFix – Corrective: Pipe Burst Repair",       "amount":  3800.00, "date": "2025-03-02", "vendor_id": techfix,     "reference_no": "INV-TF-2503A","status": "paid",    "payment_method": "bank_transfer"},
        {"category": "maintenance",  "description": "Kone Elevator – Door Sensor Replacement",       "amount":  2200.00, "date": "2025-03-05", "vendor_id": kone,        "reference_no": "INV-KN-2503", "status": "paid",    "payment_method": "cheque"},
        {"category": "maintenance",  "description": "TechFix – Fire Alarm Sensor Replacement L6",    "amount":  1800.00, "date": "2025-03-08", "vendor_id": techfix,     "reference_no": "INV-TF-2503B","status": "paid",    "payment_method": "bank_transfer"},
        {"category": "security",     "description": "SecureGuard – Feb 2025 Security Services",      "amount": 18500.00, "date": "2025-02-28", "vendor_id": secureguard, "reference_no": "INV-SG-2502", "status": "paid",    "payment_method": "bank_transfer"},
        {"category": "utilities",    "description": "SP Group – Electricity Feb 2025",                "amount": 39800.00, "date": "2025-03-05", "vendor_id": None,        "reference_no": "SP-0225",     "status": "paid",    "payment_method": "online"},
        {"category": "cleaning",     "description": "SparkClean – Mar 2025 Façade Cleaning",         "amount":  6500.00, "date": d(-5),        "vendor_id": sparkclean,  "reference_no": "INV-SC-2503", "status": "pending", "payment_method": "bank_transfer"},
        {"category": "maintenance",  "description": "TechFix – Chiller Plant Emergency Service",     "amount": 12000.00, "date": d(-2),        "vendor_id": techfix,     "reference_no": "INV-TF-2503C","status": "pending", "payment_method": None},
        {"category": "utilities",    "description": "SP Group – Electricity Mar 2025",                "amount": 41200.00, "date": d(5),         "vendor_id": None,        "reference_no": "SP-0325",     "status": "pending", "payment_method": None},
        {"category": "others",       "description": "BizSafe Audit & Certification Renewal",         "amount":  3500.00, "date": d(10),        "vendor_id": None,        "reference_no": "BCA-2025",    "status": "pending", "payment_method": None},
    ]
    for c in costs_data:
        c["building_id"] = bids
    await db.costs.insert_many(costs_data)
    print(f"Costs inserted: {len(costs_data)}")

    # ── Night Watch Duty Roster ───────────────────────────────────────
    roster_data = [
        {"date": d(-6), "shift": "night", "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "completed", "notes": "Regular patrol – no incidents."},
        {"date": d(-5), "shift": "night", "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "completed", "notes": "Regular patrol – minor loitering at G floor, resolved."},
        {"date": d(-4), "shift": "night", "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "completed", "notes": "Regular patrol – all clear."},
        {"date": d(-3), "shift": "night", "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "completed", "notes": "Regular patrol – suspicious individual reported, escorted off premises."},
        {"date": d(-2), "shift": "night", "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "completed", "notes": "Regular patrol – all clear."},
        {"date": d(-1), "shift": "night", "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "completed", "notes": "Regular patrol – all clear."},
        {"date": d(0),  "shift": "night", "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "scheduled", "notes": "Patrol + CCTV monitoring."},
        {"date": d(1),  "shift": "night", "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "scheduled", "notes": None},
        {"date": d(2),  "shift": "night", "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "scheduled", "notes": None},
        {"date": d(3),  "shift": "night", "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "scheduled", "notes": None},
        {"date": d(4),  "shift": "night", "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "scheduled", "notes": None},
        {"date": d(5),  "shift": "night", "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "scheduled", "notes": None},
        {"date": d(6),  "shift": "night", "start_time": "22:00", "end_time": "06:00", "assigned_officer_ids": [], "status": "scheduled", "notes": None},
        # Morning shift for weekdays
        {"date": d(0),  "shift": "morning", "start_time": "06:00", "end_time": "14:00", "assigned_officer_ids": [], "status": "scheduled", "notes": "Morning access control + patrol."},
        {"date": d(1),  "shift": "morning", "start_time": "06:00", "end_time": "14:00", "assigned_officer_ids": [], "status": "scheduled", "notes": None},
        {"date": d(2),  "shift": "morning", "start_time": "06:00", "end_time": "14:00", "assigned_officer_ids": [], "status": "scheduled", "notes": None},
    ]
    for r in roster_data:
        r["building_id"] = bids
    await db.roster.insert_many(roster_data)
    print(f"Roster inserted: {len(roster_data)}")

    # ── Attendance ────────────────────────────────────────────────────
    # Use vendor IDs as person_id for cleaners, secureguard for security
    attendance_data = []
    for offset in range(-13, 1):
        dt = d(offset)
        is_weekday = (TODAY + timedelta(days=offset)).weekday() < 5
        if not is_weekday:
            continue
        # Cleaner attendance
        attendance_data += [
            {"attendance_type": "cleaner",  "person_id": cleanpro,    "building_id": bids, "date": dt, "check_in_time": "07:00", "check_out_time": "15:00", "status": "present", "notes": None},
            {"attendance_type": "cleaner",  "person_id": sparkclean,  "building_id": bids, "date": dt, "check_in_time": "08:00" if offset != -3 else None, "check_out_time": "16:00" if offset != -3 else None, "status": "present" if offset != -3 else "absent", "notes": "No show" if offset == -3 else None},
        ]
        # Security attendance
        attendance_data += [
            {"attendance_type": "security", "person_id": secureguard, "building_id": bids, "date": dt, "check_in_time": "08:00", "check_out_time": "20:00", "status": "present", "notes": None},
            {"attendance_type": "security", "person_id": certis,      "building_id": bids, "date": dt, "check_in_time": "08:30" if offset != -5 else "09:15", "check_out_time": "20:00", "status": "present" if offset != -5 else "late", "notes": "Late arrival" if offset == -5 else None},
        ]
    await db.attendance.insert_many(attendance_data)
    print(f"Attendance records inserted: {len(attendance_data)}")

    print("\n✅  Seed complete! Mappletree Business City data loaded into resolveapp DB.")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
