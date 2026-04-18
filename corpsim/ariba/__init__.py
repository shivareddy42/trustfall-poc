from corpsim.ariba import tools as tools

TOOLS = {
    "ariba.list_suppliers": tools.list_suppliers,
    "ariba.get_supplier": tools.get_supplier,
    "ariba.create_supplier": tools.create_supplier,
    "ariba.update_supplier": tools.update_supplier,
    "ariba.list_pos": tools.list_pos,
    "ariba.get_po": tools.get_po,
    "ariba.create_po": tools.create_po,
    "ariba.approve_po": tools.approve_po,
    "ariba.list_payments": tools.list_payments,
    "ariba.list_pending_approvals": tools.list_pending_approvals,
}

__all__ = ["TOOLS", "tools"]
