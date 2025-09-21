"""
Feedback collection and processing module.
"""

from .collectors import FeedbackCollector
from .processors import FeedbackProcessor

__all__ = [
    "FeedbackCollector",
    "FeedbackProcessor",
]