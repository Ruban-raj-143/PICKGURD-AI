"""Escalation tool for PickGuard AI.

Creates synthetic local human-in-the-loop escalation records saved in SQLite database.
Does NOT modify inventory, modify order records, or contact external warehouse systems.
"""

import sqlite3
import os
from datetime import datetime, timezone
from typing import Any, Dict
from langchain_core.tools import tool
from backend.app.config import settings
from backend.app.models.tool_schemas import EscalationResult

# Determine database file path from config
DB_FILE = settings.database_url.replace("sqlite:///", "")
if not os.path.isabs(DB_FILE):
    DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", DB_FILE.lstrip("./")))


def _init_db() -> None:
    """Ensure escalations table exists in SQLite database."""
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS escalations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                escalation_id TEXT UNIQUE NOT NULL,
                task_id TEXT NOT NULL,
                exception_type TEXT NOT NULL,
                reason TEXT NOT NULL,
                evidence_summary TEXT NOT NULL,
                recommended_action TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def create_escalation(
    task_id: str,
    exception_type: str,
    reason: str,
    evidence_summary: str,
    recommended_action: str,
) -> Dict[str, Any]:
    """Create a local synthetic escalation record requiring human review.

    Args:
        task_id: Pick task ID triggering escalation
        exception_type: Exception classification
        reason: Operational reason for escalation
        evidence_summary: Grounding evidence summary
        recommended_action: Suggested operator action

    Returns:
        Structured dictionary matching EscalationResult schema.
    """
    _init_db()

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM escalations")
        count = cursor.fetchone()[0] + 1
        esc_id = f"ESC-{count:04d}"

        cursor.execute(
            """
            INSERT INTO escalations (
                escalation_id, task_id, exception_type, reason, evidence_summary, recommended_action, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                esc_id,
                task_id,
                exception_type,
                reason,
                evidence_summary,
                recommended_action,
                "PENDING_HUMAN_REVIEW",
                now_str,
            ),
        )
        conn.commit()

    return EscalationResult(
        success=True,
        escalation_id=esc_id,
        status="PENDING_HUMAN_REVIEW",
        task_id=task_id,
        exception_type=exception_type,
        reason=reason,
        evidence_summary=evidence_summary,
        recommended_action=recommended_action,
        created_at=now_str,
    ).model_dump()


@tool("create_escalation")
def create_escalation_tool(
    task_id: str,
    exception_type: str,
    reason: str,
    evidence_summary: str,
    recommended_action: str,
) -> Dict[str, Any]:
    """Log a synthetic escalation record for human supervisor review."""
    return create_escalation(
        task_id=task_id,
        exception_type=exception_type,
        reason=reason,
        evidence_summary=evidence_summary,
        recommended_action=recommended_action,
    )
