from corpsim.itsm import tools as tools

TOOLS = {
    "itsm.list_incidents": tools.list_incidents,
    "itsm.get_incident": tools.get_incident,
    "itsm.create_incident": tools.create_incident,
    "itsm.update_incident": tools.update_incident,
    "itsm.list_approvals": tools.list_approvals,
    "itsm.get_user": tools.get_user,
    "itsm.search_users": tools.search_users,
    "itsm.grant_group_membership": tools.grant_group_membership,
}

__all__ = ["TOOLS", "tools"]
