"""
Seed script: creates sample clients & contracts, then patches existing data.
Run from the backend/ directory:
    python seed_clients_contracts.py
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "resolveapp")


async def run():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    # ── 1. Clients ────────────────────────────────────────────────────────────
    clients_data = [
        {
            "name": "SkyProperty Pte Ltd",
            "registration_number": "202301234A",
            "industry": "Property Management",
            "website": "https://skyproperty.sg",
            "email": "contact@skyproperty.sg",
            "phone": "+65 6123 4567",
            "address_street": "1 Raffles Place #20-01",
            "address_city": "Singapore",
            "address_state": "",
            "address_country": "Singapore",
            "address_postal": "048616",
            "contacts": [
                {"name": "James Tan", "role": "Account Manager", "email": "james@skyproperty.sg", "phone": "+65 9111 2222"},
                {"name": "Sarah Lim", "role": "Operations Director", "email": "sarah@skyproperty.sg", "phone": "+65 9333 4444"},
            ],
            "status": "active",
            "notes": "Primary property management client covering central business district.",
        },
        {
            "name": "GreenSpace Corp",
            "registration_number": "202205678B",
            "industry": "Commercial Real Estate",
            "website": "https://greenspace.com.sg",
            "email": "info@greenspace.com.sg",
            "phone": "+65 6234 5678",
            "address_street": "10 Marina Boulevard #15-10",
            "address_city": "Singapore",
            "address_state": "",
            "address_country": "Singapore",
            "address_postal": "018983",
            "contacts": [
                {"name": "David Ng", "role": "Facilities Manager", "email": "david@greenspace.com.sg", "phone": "+65 9555 6666"},
            ],
            "status": "active",
            "notes": "Commercial real estate client with focus on green building standards.",
        },
        {
            "name": "Urban Living Management",
            "registration_number": "201912345C",
            "industry": "Residential Management",
            "website": "https://urbanliving.sg",
            "email": "hello@urbanliving.sg",
            "phone": "+65 6345 6789",
            "address_street": "50 Orchard Road #08-05",
            "address_city": "Singapore",
            "address_state": "",
            "address_country": "Singapore",
            "address_postal": "238893",
            "contacts": [
                {"name": "Michelle Wong", "role": "Property Manager", "email": "michelle@urbanliving.sg", "phone": "+65 9777 8888"},
                {"name": "Kevin Chia", "role": "Technical Lead", "email": "kevin@urbanliving.sg", "phone": "+65 9999 0000"},
            ],
            "status": "active",
            "notes": "Residential property management across multiple estates.",
        },
    ]

    await db.clients.delete_many({})
    await db.contracts.delete_many({})
    print("  Cleared existing clients and contracts")

    client_ids = {}
    for c in clients_data:
        result = await db.clients.insert_one(c)
        client_ids[c["name"]] = result.inserted_id
        print(f"  Created client: {c['name']}")

    # ── 2. Buildings: assign clients ─────────────────────────────────────────
    buildings = await db.buildings.find().to_list(100)
    building_ids = [b["_id"] for b in buildings]
    building_id_strs = [str(b["_id"]) for b in buildings]

    # Distribute buildings across clients
    client_names = list(client_ids.keys())
    for i, b in enumerate(buildings):
        assigned_client = client_names[i % len(client_names)]
        await db.buildings.update_one(
            {"_id": b["_id"]},
            {"$set": {"client_id": str(client_ids[assigned_client])}}
        )
    print(f"  Patched {len(buildings)} buildings with client_id")

    # ── 3. Contracts ─────────────────────────────────────────────────────────
    # Assign 1/3 of buildings to each contract (or all if < 3 buildings)
    chunk = max(1, len(building_id_strs) // 3)
    contracts_data = [
        {
            "contract_number": "CON-2024-001",
            "client_id": str(client_ids["SkyProperty Pte Ltd"]),
            "title": "Annual Facility Management Agreement",
            "description": "Comprehensive facility management covering cleaning, preventive and corrective maintenance.",
            "building_ids": building_id_strs[:chunk],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "value": 480000.00,
            "currency": "SGD",
            "status": "active",
            "notes": "Includes 24/7 emergency response SLA.",
        },
        {
            "contract_number": "CON-2024-002",
            "client_id": str(client_ids["GreenSpace Corp"]),
            "title": "Cleaning & Maintenance Contract",
            "description": "Scheduled cleaning and preventive maintenance services.",
            "building_ids": building_id_strs[chunk:chunk*2],
            "start_date": "2024-03-01",
            "end_date": "2025-02-28",
            "value": 240000.00,
            "currency": "SGD",
            "status": "active",
            "notes": "Green-certified cleaning products required.",
        },
        {
            "contract_number": "CON-2024-003",
            "client_id": str(client_ids["Urban Living Management"]),
            "title": "Residential Services Contract",
            "description": "Full-service residential facility management.",
            "building_ids": building_id_strs[chunk*2:],
            "start_date": "2024-06-01",
            "end_date": "2025-05-31",
            "value": 360000.00,
            "currency": "SGD",
            "status": "active",
            "notes": "Includes concierge and security coordination.",
        },
    ]

    contract_ids = {}
    for c in contracts_data:
        result = await db.contracts.insert_one(c)
        contract_ids[c["contract_number"]] = result.inserted_id
        print(f"  Created contract: {c['contract_number']}")

    # ── 4. Patch existing records with contract_id ────────────────────────────
    # Map building_id → contract_id
    building_to_contract = {}

    all_contracts = await db.contracts.find().to_list(100)
    for con in all_contracts:
        for bid in (con.get("building_ids") or []):
            building_to_contract[bid] = str(con["_id"])

    async def patch_collection(col_name):
        docs = await db[col_name].find({}).to_list(1000)
        patched = 0
        for doc in docs:
            cid = building_to_contract.get(str(doc.get("building_id", "")))
            if cid:
                await db[col_name].update_one({"_id": doc["_id"]}, {"$set": {"contract_id": cid}})
                patched += 1
        print(f"  Patched {patched}/{len(docs)} {col_name}")

    await patch_collection("cleaning_schedules")
    await patch_collection("preventive_maintenance")
    await patch_collection("corrective_maintenance")
    await patch_collection("cases")

    client.close()
    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(run())
