from fastapi import APIRouter, Depends
from app.database import get_db
from app.utils.auth import get_current_user
from datetime import datetime, timezone

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard")
async def dashboard_stats(_=Depends(get_current_user)):
    db = get_db()
    total_buildings = await db.buildings.count_documents({})
    total_units = await db.units.count_documents({})
    occupied_units = await db.units.count_documents({"status": "occupied"})
    open_cases = await db.cases.count_documents({"status": {"$in": ["open", "in_progress"]}})
    open_cm = await db.corrective_maintenance.count_documents({"status": {"$in": ["open", "in_progress"]}})
    overdue_pm = await db.preventive_maintenance.count_documents({"status": "overdue"})

    # Current month cost
    now = datetime.now(timezone.utc)
    month_prefix = now.strftime("%Y-%m")
    monthly_costs = await db.costs.find({"date": {"$regex": f"^{month_prefix}"}}).to_list(1000)
    monthly_total = sum(c.get("amount", 0) for c in monthly_costs)

    # Pending vendors
    active_vendors = await db.vendors.count_documents({"status": "active"})

    return {
        "total_buildings": total_buildings,
        "total_units": total_units,
        "occupied_units": occupied_units,
        "occupancy_rate": round(occupied_units / total_units * 100, 1) if total_units else 0,
        "open_cases": open_cases,
        "open_corrective_maintenance": open_cm,
        "overdue_preventive_maintenance": overdue_pm,
        "monthly_cost": monthly_total,
        "active_vendors": active_vendors,
    }


@router.get("/cases-by-status")
async def cases_by_status(_=Depends(get_current_user)):
    db = get_db()
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    results = await db.cases.aggregate(pipeline).to_list(20)
    return [{"status": r["_id"], "count": r["count"]} for r in results]


@router.get("/costs-by-month")
async def costs_by_month(year: int = None, _=Depends(get_current_user)):
    db = get_db()
    if not year:
        year = datetime.now(timezone.utc).year
    pipeline = [
        {"$match": {"date": {"$regex": f"^{year}"}}},
        {"$group": {
            "_id": {"month": {"$substr": ["$date", 0, 7]}, "category": "$category"},
            "total": {"$sum": "$amount"}
        }},
        {"$sort": {"_id.month": 1}}
    ]
    results = await db.costs.aggregate(pipeline).to_list(200)
    # Reshape for frontend
    months = {}
    for r in results:
        month = r["_id"]["month"]
        category = r["_id"]["category"]
        if month not in months:
            months[month] = {"month": month}
        months[month][category] = r["total"]
    return list(months.values())


@router.get("/maintenance-stats")
async def maintenance_stats(_=Depends(get_current_user)):
    db = get_db()
    pm_by_status = await db.preventive_maintenance.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]).to_list(20)
    cm_by_status = await db.corrective_maintenance.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]).to_list(20)
    return {
        "preventive": [{"status": r["_id"], "count": r["count"]} for r in pm_by_status],
        "corrective": [{"status": r["_id"], "count": r["count"]} for r in cm_by_status],
    }


@router.get("/attendance-summary")
async def attendance_summary(month: str = None, _=Depends(get_current_user)):
    db = get_db()
    if not month:
        month = datetime.now(timezone.utc).strftime("%Y-%m")
    pipeline = [
        {"$match": {"date": {"$regex": f"^{month}"}}},
        {"$group": {
            "_id": {"type": "$attendance_type", "status": "$status"},
            "count": {"$sum": 1}
        }}
    ]
    results = await db.attendance.aggregate(pipeline).to_list(50)
    return [{"type": r["_id"]["type"], "status": r["_id"]["status"], "count": r["count"]} for r in results]


@router.get("/recent-cases")
async def recent_cases(limit: int = 5, _=Depends(get_current_user)):
    db = get_db()
    cases = await db.cases.find().sort("created_at", -1).limit(limit).to_list(limit)
    result = []
    for c in cases:
        building = await db.buildings.find_one({"_id": c["building_id"]}) if c.get("building_id") else None
        result.append({
            "id": str(c["_id"]),
            "case_number": c.get("case_number"),
            "title": c.get("title"),
            "status": c.get("status"),
            "priority": c.get("priority"),
            "building_name": building["name"] if building else None,
            "created_at": c.get("created_at"),
        })
    return result
