from datetime import datetime
from enum import Enum

class Action(Enum):
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    MERGE = "merge"

def create_event(author, from_branch, to_branch, action, request_id):
    """
    Function to create an event object to be inserted into the database.
    """
    try:
        return {
            "author": author,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": datetime.utcnow().isoformat(),
            "action": action.value,
            "request_id": request_id,
        }
    except Exception as e:
        print(f"Error creating event: {e}")
        return None
