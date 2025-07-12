"""Import *every* model class once so SQLAlchemy knows them.

Do NOT import Flask extensions, blueprints, etc. – only models.
"""

from .user         import User           # noqa: F401
from .question     import Question       # noqa: F401
from .answer       import Answer         # noqa: F401
from .tag          import Tag            # noqa: F401
from .vote         import Vote, VoteType # noqa: F401
from .notification import Notification   # noqa: F401

__all__ = [
    "User",
    "Question",
    "Answer",
    "Tag",
    "Vote",
    "VoteType",
    "Notification",
]
