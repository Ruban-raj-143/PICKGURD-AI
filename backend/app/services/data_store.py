"""Data access layer for PickGuard AI synthetic warehouse datasets.

Loads locations, inventory, pick tasks, and historical incidents from CSV files
and provides efficient in-memory indexed access for operational tools.
"""

import os
import pandas as pd
from typing import Any, Dict, List, Optional

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data"))


class DataStore:
    """Singleton data store loading synthetic CSV datasets once into memory."""

    _instance: Optional["DataStore"] = None

    def __new__(cls) -> "DataStore":
        if cls._instance is None:
            cls._instance = super(DataStore, cls).__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self) -> None:
        """Load CSV files and create lookup indices."""
        locations_path = os.path.join(DATA_DIR, "locations.csv")
        inventory_path = os.path.join(DATA_DIR, "inventory.csv")
        pick_tasks_path = os.path.join(DATA_DIR, "pick_tasks.csv")
        incidents_path = os.path.join(DATA_DIR, "incidents.csv")

        self.df_loc = pd.read_csv(locations_path).fillna("")
        self.df_inv = pd.read_csv(inventory_path).fillna("")
        self.df_task = pd.read_csv(pick_tasks_path).fillna("")
        self.df_inc = pd.read_csv(incidents_path).fillna("")

        # Create quick lookup dicts keyed by primary keys
        self.locations_map: Dict[str, Dict[str, Any]] = {
            row["location_id"]: row.to_dict() for _, row in self.df_loc.iterrows()
        }
        self.inventory_map: Dict[str, Dict[str, Any]] = {
            row["item_id"]: row.to_dict() for _, row in self.df_inv.iterrows()
        }
        self.tasks_map: Dict[str, Dict[str, Any]] = {
            row["task_id"]: row.to_dict() for _, row in self.df_task.iterrows()
        }

    def reload(self) -> None:
        """Reload datasets from disk (useful for tests)."""
        self._load_data()

    def get_inventory(self, item_id: str, location_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve inventory record by item_id and optional location_id."""
        if not item_id:
            return None

        # Check by primary item_id
        item = self.inventory_map.get(item_id)
        if item:
            if location_id and item["location_id"] != location_id:
                # Search if there is another matching record for item_id at location_id
                matches = self.df_inv[(self.df_inv["item_id"] == item_id) & (self.df_inv["location_id"] == location_id)]
                if not matches.empty:
                    return matches.iloc[0].to_dict()
                return None
            return item

        # If item_id not found directly, check if location_id specified
        if location_id:
            matches = self.df_inv[(self.df_inv["item_id"] == item_id) & (self.df_inv["location_id"] == location_id)]
            if not matches.empty:
                return matches.iloc[0].to_dict()

        return None

    def get_pick_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve pick task record by task_id."""
        if not task_id:
            return None
        return self.tasks_map.get(task_id)

    def get_location(self, location_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve location record by location_id."""
        if not location_id:
            return None
        return self.locations_map.get(location_id)

    def search_incidents(
        self,
        item_id: Optional[str] = None,
        location_id: Optional[str] = None,
        exception_type: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search historical incidents using deterministic ranking rules.

        Ranking Priority:
        1. Exact item_id + location_id + exception_type
        2. Exact item_id + exception_type
        3. Exact location_id + exception_type
        4. Exact exception_type
        5. Fallback matches on item_id or location_id
        """
        df = self.df_inc.copy()

        if df.empty:
            return []

        scored_rows = []
        for _, row in df.iterrows():
            score = 0
            row_item = row["item_id"]
            row_loc = row["location_id"]
            row_exc = row["exception_type"]

            match_item = item_id and row_item == item_id
            match_loc = location_id and row_loc == location_id
            match_exc = exception_type and row_exc == exception_type

            if match_item and match_loc and match_exc:
                score = 100
            elif match_item and match_exc:
                score = 80
            elif match_loc and match_exc:
                score = 60
            elif match_exc:
                score = 40
            elif match_item or match_loc:
                score = 20
            else:
                score = 0

            if score > 0:
                rec = row.to_dict()
                rec["_score"] = score
                scored_rows.append(rec)

        # Sort by score descending, then by created_at descending
        scored_rows.sort(key=lambda r: (r["_score"], r.get("created_at", "")), reverse=True)

        # Strip internal score before returning
        results = []
        for r in scored_rows[:limit]:
            clean_r = {k: v for k, v in r.items() if k != "_score"}
            results.append(clean_r)

        return results


data_store = DataStore()
