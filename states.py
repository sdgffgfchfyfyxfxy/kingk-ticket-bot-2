from enum import Enum, auto

class TicketState(Enum):
    GET_TITLE = auto()
    COLLECT_MESSAGES = auto()
    CONFIRM_TICKET = auto()
    EDIT_TITLE = auto()
    EDIT_MSG_1 = auto()
    EDIT_MSG_2 = auto()
    EDIT_MSG_3 = auto()
    VIEW_USER_TICKET = auto()
    USER_REPLY = auto()
    ADMIN_REPLY = auto()