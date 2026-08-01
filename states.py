from enum import Enum, auto

class TicketState(Enum):
    GET_TITLE = auto()
    COLLECT_MESSAGES = auto()
    CONFIRM_TICKET = auto()
    EDIT_TITLE = auto()