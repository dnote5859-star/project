from pymongo import MongoClient, ReturnDocument
from bson.objectid import ObjectId
from datetime import datetime
import config

class DBHandler:
    def __init__(self, uri=None):
        self.client = MongoClient(uri or config.MONGO_URI)
        # get_default_database() can raise if URI doesn't include a db name.
        # Also Database objects don't support truth testing, so compare with None.
        try:
            default_db = self.client.get_default_database()
        except Exception:
            default_db = None
        self.db = default_db if default_db is not None else self.client["trucker_profit"]

        # collections
        self.drivers = self.db.drivers
        self.units = self.db.units
        self.trips = self.db.trips
        self.settings = self.db.settings

        # ensure a settings document exists
        if self.settings.count_documents({}) == 0:
            self.settings.insert_one({
                "exchange_rate": config.DEFAULT_EXCHANGE_RATE,
                "primary_currency": "USD",
                "created_at": datetime.utcnow()
            })

    # ---------- Settings ----------
    def get_exchange_rate(self):
        doc = self.settings.find_one({}, sort=[("_id", 1)])
        return doc.get("exchange_rate", config.DEFAULT_EXCHANGE_RATE)

    def set_exchange_rate(self, rate):
        return self.settings.find_one_and_update(
            {},
            {"$set": {"exchange_rate": float(rate)}},
            return_document=ReturnDocument.AFTER
        )

    def get_primary_currency(self):
        doc = self.settings.find_one({}, sort=[("_id", 1)])
        return doc.get("primary_currency", "USD")

    def set_primary_currency(self, cur):
        return self.settings.find_one_and_update(
            {},
            {"$set": {"primary_currency": cur}},
            return_document=ReturnDocument.AFTER
        )

    # ---------- Drivers ----------
    def list_drivers(self, filter_query=None):
        q = filter_query or {}
        return list(self.drivers.find(q))

    def get_driver(self, driver_id):
        try:
            return self.drivers.find_one({"_id": ObjectId(driver_id)})
        except Exception:
            return None

    def create_driver(self, driver_doc):
        driver_doc.setdefault("created_at", datetime.utcnow())
        return self.drivers.insert_one(driver_doc)

    def update_driver(self, driver_id, fields):
        return self.drivers.find_one_and_update(
            {"_id": ObjectId(driver_id)},
            {"$set": fields},
            return_document=ReturnDocument.AFTER
        )

    # ---------- Units ----------
    def list_units(self, filter_query=None):
        q = filter_query or {}
        return list(self.units.find(q))

    def get_unit(self, unit_id):
        try:
            return self.units.find_one({"_id": ObjectId(unit_id)})
        except Exception:
            return None

    def create_unit(self, unit_doc):
        unit_doc.setdefault("created_at", datetime.utcnow())
        unit_doc.setdefault("expenses", [])
        return self.units.insert_one(unit_doc)

    def add_unit_expense(self, unit_id, expense):
        expense.setdefault("created_at", datetime.utcnow())
        return self.units.find_one_and_update(
            {"_id": ObjectId(unit_id)},
            {"$push": {"expenses": expense}},
            return_document=ReturnDocument.AFTER
        )

    # ---------- Trips ----------
    def list_trips(self, filter_query=None):
        q = filter_query or {}
        return list(self.trips.find(q))

    def get_trip(self, trip_id):
        try:
            return self.trips.find_one({"_id": ObjectId(trip_id)})
        except Exception:
            return None

    def create_trip(self, trip_doc):
        trip_doc.setdefault("created_at", datetime.utcnow())
        trip_doc.setdefault("expenses", [])
        trip_doc.setdefault("status", "active")
        return self.trips.insert_one(trip_doc)

    def add_trip_expense(self, trip_id, expense):
        expense.setdefault("created_at", datetime.utcnow())
        return self.trips.find_one_and_update(
            {"_id": ObjectId(trip_id)},
            {"$push": {"expenses": expense}},
            return_document=ReturnDocument.AFTER
        )

    def update_trip(self, trip_id, update_fields):
        return self.trips.find_one_and_update(
            {"_id": ObjectId(trip_id)},
            {"$set": update_fields},
            return_document=ReturnDocument.AFTER
        )

    # ---------- Seed helper ----------
    def seed_initial_data(self, seed):
        if self.drivers.count_documents({}) == 0:
            for d in seed.get("drivers", []):
                doc = {
                    "name": d.get("name"),
                    "email": d.get("email"),
                    "phone": d.get("phone"),
                    "password_hash": d.get("password_hash"),
                    "created_at": datetime.utcnow()
                }
                self.drivers.insert_one(doc)

        if self.units.count_documents({}) == 0:
            for u in seed.get("units", []):
                self.units.insert_one({
                    "number": u.get("number"),
                    "make": u.get("make"),
                    "model": u.get("model"),
                    "expenses": [],
                    "created_at": datetime.utcnow()
                })

        if self.trips.count_documents({}) == 0:
            for t in seed.get("trips", []):
                t_doc = {
                    "trip_number": t.get("tripNumber"),
                    "driver_id": None,
                    "unit_id": None,
                    "pickup_date": t.get("pickupDate"),
                    "pickup_city": t.get("pickupCity"),
                    "pickup_state": t.get("pickupState"),
                    "delivery_date": t.get("deliveryDate"),
                    "delivery_city": t.get("deliveryCity"),
                    "delivery_state": t.get("deliveryState"),
                    "payment_usd": t.get("paymentUSD"),
                    "payment_cad": t.get("paymentCAD"),
                    "status": t.get("status", "active"),
                    "expenses": [],
                    "created_at": datetime.fromisoformat(t.get("createdAt").replace("Z", "+00:00")) if t.get("createdAt") else datetime.utcnow()
                }
                self.trips.insert_one(t_doc)

        if seed.get("exchangeRate"):
            self.set_exchange_rate(seed.get("exchangeRate"))