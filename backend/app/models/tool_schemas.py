"""Pydantic schemas for PickGuard AI operational tool inputs and outputs."""

from typing import List, Optional
from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# 1. INVENTORY TOOL SCHEMAS
# -----------------------------------------------------------------------------
class InventoryResult(BaseModel):
    """Structured response from inventory tool lookup."""

    found: bool = Field(description="Whether the inventory record was found")
    item_id: Optional[str] = Field(default=None, description="Item identifier")
    location_id: Optional[str] = Field(default=None, description="Storage location ID")
    sku: Optional[str] = Field(default=None, description="Stock Keeping Unit")
    item_name: Optional[str] = Field(default=None, description="Product item name")
    category: Optional[str] = Field(default=None, description="Product category")
    system_quantity: Optional[int] = Field(default=None, description="System recorded quantity")
    available_quantity: Optional[int] = Field(default=None, description="Pickable available quantity")
    reserved_quantity: Optional[int] = Field(default=None, description="Reserved order quantity")
    inventory_status: Optional[str] = Field(default=None, description="Inventory status code")
    last_scan_timestamp: Optional[str] = Field(default=None, description="Timestamp of last scanner audit")
    last_movement_timestamp: Optional[str] = Field(default=None, description="Timestamp of last stock transfer")
    error_code: Optional[str] = Field(default=None, description="Error code if not found")
    message: Optional[str] = Field(default=None, description="Human readable message")


# -----------------------------------------------------------------------------
# 2. PICK TASK TOOL SCHEMAS
# -----------------------------------------------------------------------------
class PickTaskResult(BaseModel):
    """Structured response from pick task tool lookup."""

    found: bool = Field(description="Whether the pick task was found")
    task_id: Optional[str] = Field(default=None, description="Pick task identifier")
    order_id: Optional[str] = Field(default=None, description="Order identifier")
    item_id: Optional[str] = Field(default=None, description="Target item identifier")
    expected_location: Optional[str] = Field(default=None, description="Expected bin location")
    required_quantity: Optional[int] = Field(default=None, description="Required pick line quantity")
    priority: Optional[str] = Field(default=None, description="Task priority level")
    status: Optional[str] = Field(default=None, description="Pick task execution status")
    created_at: Optional[str] = Field(default=None, description="Task dispatch timestamp")
    assigned_operator: Optional[str] = Field(default=None, description="Assigned operator ID")
    error_code: Optional[str] = Field(default=None, description="Error code if not found")
    message: Optional[str] = Field(default=None, description="Human readable message")


# -----------------------------------------------------------------------------
# 3. LOCATION TOOL SCHEMAS
# -----------------------------------------------------------------------------
class LocationResult(BaseModel):
    """Structured response from location tool lookup."""

    found: bool = Field(description="Whether the location was found")
    location_id: Optional[str] = Field(default=None, description="Bin location ID")
    zone: Optional[str] = Field(default=None, description="Warehouse zone ID")
    aisle: Optional[str] = Field(default=None, description="Aisle designation")
    rack: Optional[str] = Field(default=None, description="Rack designation")
    bin: Optional[str] = Field(default=None, description="Bin designation")
    status: Optional[str] = Field(default=None, description="Location operational status")
    capacity: Optional[int] = Field(default=None, description="Max bin storage capacity")
    neighbouring_locations: List[str] = Field(default_factory=list, description="Adjacent bin location IDs")
    error_code: Optional[str] = Field(default=None, description="Error code if not found")
    message: Optional[str] = Field(default=None, description="Human readable message")


# -----------------------------------------------------------------------------
# 4. INCIDENT TOOL SCHEMAS
# -----------------------------------------------------------------------------
class IncidentItem(BaseModel):
    """Individual historical exception incident record."""

    incident_id: str
    task_id: str
    item_id: str
    location_id: str
    exception_type: str
    description: str
    observed_quantity: int
    expected_quantity: int
    previous_location: str
    resolution: str
    resolution_category: str
    resolution_time_seconds: int
    operator_id: str
    created_at: str


class IncidentSearchResult(BaseModel):
    """Structured response from historical incident search tool."""

    count: int = Field(description="Total matching incidents returned")
    incidents: List[IncidentItem] = Field(default_factory=list, description="List of historical incidents")
    error_code: Optional[str] = Field(default=None, description="Error code if query invalid")
    message: Optional[str] = Field(default=None, description="Human readable message")


# -----------------------------------------------------------------------------
# 5. SOP INTERFACE STUB SCHEMAS
# -----------------------------------------------------------------------------
class SOPResult(BaseModel):
    """Structured response stub for Phase 4 SOP retrieval."""

    status: str = Field(default="NOT_IMPLEMENTED", description="RAG status code")
    message: str = Field(
        default="SOP retrieval will be implemented in Phase 4.",
        description="Informational status message",
    )


# -----------------------------------------------------------------------------
# 6. ESCALATION TOOL SCHEMAS
# -----------------------------------------------------------------------------
class EscalationInput(BaseModel):
    """Input payload to create human-in-the-loop escalation."""

    task_id: str
    exception_type: str
    reason: str
    evidence_summary: str
    recommended_action: str


class EscalationResult(BaseModel):
    """Structured response from escalation creation tool."""

    success: bool
    escalation_id: str
    status: str = Field(default="PENDING_HUMAN_REVIEW")
    task_id: str
    exception_type: str
    reason: str
    evidence_summary: str
    recommended_action: str
    created_at: str
    message: str = Field(
        default="Synthetic human review request recorded locally. No inventory or external systems modified."
    )
