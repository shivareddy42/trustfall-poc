from corpsim.email import tools as tools

TOOLS = {
    "email.list_messages": tools.list_messages,
    "email.get_message": tools.get_message,
    "email.send_message": tools.send_message,
    "email.draft_message": tools.draft_message,
}

__all__ = ["TOOLS", "tools"]
