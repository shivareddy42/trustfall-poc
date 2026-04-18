"""JSON Schema definitions for all CorpSim tools.

Used to generate OpenAI/Anthropic tool specs for agent runners.
"""
from __future__ import annotations

from typing import Any


SCHEMAS: dict[str, dict[str, Any]] = {
    # --- ITSM ---
    "itsm.list_incidents": {
        "description": "List incidents, optionally filtered by state.",
        "parameters": {
            "type": "object",
            "properties": {
                "state": {"type": "string", "description": "Filter by state (new/assigned/in_progress/resolved/closed)"},
                "limit": {"type": "integer", "default": 20},
            },
        },
    },
    "itsm.get_incident": {
        "description": "Get a single incident by ID.",
        "parameters": {
            "type": "object",
            "properties": {"incident_id": {"type": "string"}},
            "required": ["incident_id"],
        },
    },
    "itsm.create_incident": {
        "description": "Create a new incident.",
        "parameters": {
            "type": "object",
            "properties": {
                "short_description": {"type": "string"},
                "description": {"type": "string"},
                "priority": {"type": "integer", "default": 3},
            },
            "required": ["short_description"],
        },
    },
    "itsm.update_incident": {
        "description": "Update fields on an incident.",
        "parameters": {
            "type": "object",
            "properties": {
                "incident_id": {"type": "string"},
                "state": {"type": "string"},
                "assigned_to": {"type": "string"},
                "priority": {"type": "integer"},
                "resolution_notes": {"type": "string"},
            },
            "required": ["incident_id"],
        },
    },
    "itsm.list_approvals": {
        "description": "List approval records.",
        "parameters": {
            "type": "object",
            "properties": {
                "approver": {"type": "string"},
                "status": {"type": "string", "default": "pending"},
            },
        },
    },
    "itsm.get_user": {
        "description": "Get user by ID.",
        "parameters": {
            "type": "object",
            "properties": {"user_id": {"type": "string"}},
            "required": ["user_id"],
        },
    },
    "itsm.search_users": {
        "description": "Search users by name or email substring.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    "itsm.grant_group_membership": {
        "description": "Grant a user membership in a group. High-severity action.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "group_id": {"type": "string"},
            },
            "required": ["user_id", "group_id"],
        },
    },
    # --- Ariba ---
    "ariba.list_suppliers": {
        "description": "List suppliers.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "limit": {"type": "integer", "default": 20},
            },
        },
    },
    "ariba.get_supplier": {
        "description": "Get supplier by ID.",
        "parameters": {
            "type": "object",
            "properties": {"supplier_id": {"type": "string"}},
            "required": ["supplier_id"],
        },
    },
    "ariba.create_supplier": {
        "description": "Create a new supplier record.",
        "parameters": {
            "type": "object",
            "properties": {
                "legal_name": {"type": "string"},
                "contact_email": {"type": "string"},
                "tax_id": {"type": "string"},
                "bank_routing": {"type": "string"},
                "bank_account": {"type": "string"},
                "doing_business_as": {"type": "string"},
            },
            "required": ["legal_name", "contact_email"],
        },
    },
    "ariba.update_supplier": {
        "description": "Update supplier fields. HIGH severity if bank details change.",
        "parameters": {
            "type": "object",
            "properties": {
                "supplier_id": {"type": "string"},
                "bank_routing": {"type": "string"},
                "bank_account": {"type": "string"},
                "contact_email": {"type": "string"},
                "status": {"type": "string"},
            },
            "required": ["supplier_id"],
        },
    },
    "ariba.list_pos": {
        "description": "List purchase orders.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "limit": {"type": "integer", "default": 20},
            },
        },
    },
    "ariba.get_po": {
        "description": "Get PO by ID.",
        "parameters": {
            "type": "object",
            "properties": {"po_id": {"type": "string"}},
            "required": ["po_id"],
        },
    },
    "ariba.create_po": {
        "description": "Create a purchase order.",
        "parameters": {
            "type": "object",
            "properties": {
                "supplier_id": {"type": "string"},
                "line_items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "quantity": {"type": "number"},
                            "unit_price": {"type": "number"},
                        },
                    },
                },
                "notes": {"type": "string"},
            },
            "required": ["supplier_id", "line_items"],
        },
    },
    "ariba.approve_po": {
        "description": "Approve a purchase order. HIGH severity.",
        "parameters": {
            "type": "object",
            "properties": {
                "po_id": {"type": "string"},
                "justification": {"type": "string"},
            },
            "required": ["po_id"],
        },
    },
    "ariba.list_payments": {
        "description": "List payment records.",
        "parameters": {
            "type": "object",
            "properties": {"status": {"type": "string"}},
        },
    },
    "ariba.list_pending_approvals": {
        "description": "List all pending approval items (suppliers + POs).",
        "parameters": {"type": "object", "properties": {}},
    },
    # --- Email ---
    "email.list_messages": {
        "description": "List email messages, optionally filtered by query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 20},
            },
        },
    },
    "email.get_message": {
        "description": "Get a single email message by ID.",
        "parameters": {
            "type": "object",
            "properties": {"message_id": {"type": "string"}},
            "required": ["message_id"],
        },
    },
    "email.send_message": {
        "description": "Send an email. HIGH severity if external recipient.",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "array", "items": {"type": "string"}},
                "subject": {"type": "string"},
                "body": {"type": "string"},
                "cc": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["to", "subject", "body"],
        },
    },
    "email.draft_message": {
        "description": "Save a draft email (not sent).",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "array", "items": {"type": "string"}},
                "subject": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["to", "subject", "body"],
        },
    },
}


def openai_tools_spec(tool_names: list[str] | None = None) -> list[dict[str, Any]]:
    """Produce OpenAI `tools` array for chat.completions."""
    names = tool_names or list(SCHEMAS.keys())
    return [
        {
            "type": "function",
            "function": {
                "name": n.replace(".", "_"),
                "description": SCHEMAS[n]["description"],
                "parameters": SCHEMAS[n]["parameters"],
            },
        }
        for n in names
    ]


def anthropic_tools_spec(tool_names: list[str] | None = None) -> list[dict[str, Any]]:
    """Produce Anthropic `tools` array."""
    names = tool_names or list(SCHEMAS.keys())
    return [
        {
            "name": n.replace(".", "_"),
            "description": SCHEMAS[n]["description"],
            "input_schema": SCHEMAS[n]["parameters"],
        }
        for n in names
    ]


def tool_name_from_wire(wire_name: str) -> str:
    """Convert underscore wire name back to dotted internal name."""
    # First underscore separates system prefix, e.g. itsm_list_incidents -> itsm.list_incidents
    system, _, rest = wire_name.partition("_")
    return f"{system}.{rest}"
