"""
Feedback collection mechanisms.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class FeedbackType(Enum):
    """Types of feedback."""
    PERFORMANCE = "performance"
    QUALITY = "quality"
    USER_SATISFACTION = "user_satisfaction"
    ERROR_REPORT = "error_report"
    SUGGESTION = "suggestion"


class FeedbackSource(Enum):
    """Sources of feedback."""
    USER = "user"
    SYSTEM = "system"
    AGENT = "agent"
    AUTOMATED = "automated"


@dataclass
class Feedback:
    """Represents a piece of feedback."""
    feedback_id: str
    timestamp: datetime
    source: FeedbackSource
    feedback_type: FeedbackType
    target_type: str  # "agent", "strategy", "campaign", "system"
    target_id: str
    rating: Optional[float] = None
    comment: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class FeedbackCollector:
    """Collects feedback from various sources."""
    
    def __init__(self):
        """Initialize feedback collector."""
        self.feedback_items: List[Feedback] = []
        self.feedback_hooks: Dict[str, List[callable]] = {}
    
    def collect_user_feedback(
        self,
        feedback_id: str,
        target_type: str,
        target_id: str,
        feedback_type: FeedbackType,
        rating: Optional[float] = None,
        comment: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Collect feedback from a user."""
        feedback = Feedback(
            feedback_id=feedback_id,
            timestamp=datetime.now(),
            source=FeedbackSource.USER,
            feedback_type=feedback_type,
            target_type=target_type,
            target_id=target_id,
            rating=rating,
            comment=comment,
            metadata=metadata or {}
        )
        
        self.feedback_items.append(feedback)
        self._trigger_hooks(feedback)
        
        return feedback_id
    
    def collect_system_feedback(
        self,
        feedback_id: str,
        target_type: str,
        target_id: str,
        feedback_type: FeedbackType,
        rating: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Collect automated system feedback."""
        feedback = Feedback(
            feedback_id=feedback_id,
            timestamp=datetime.now(),
            source=FeedbackSource.SYSTEM,
            feedback_type=feedback_type,
            target_type=target_type,
            target_id=target_id,
            rating=rating,
            metadata=metadata or {}
        )
        
        self.feedback_items.append(feedback)
        self._trigger_hooks(feedback)
        
        return feedback_id
    
    def collect_agent_feedback(
        self,
        feedback_id: str,
        agent_id: str,
        target_type: str,
        target_id: str,
        feedback_type: FeedbackType,
        rating: Optional[float] = None,
        comment: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Collect feedback from an agent about its own performance or other agents."""
        feedback = Feedback(
            feedback_id=feedback_id,
            timestamp=datetime.now(),
            source=FeedbackSource.AGENT,
            feedback_type=feedback_type,
            target_type=target_type,
            target_id=target_id,
            rating=rating,
            comment=comment,
            metadata={**(metadata or {}), "source_agent_id": agent_id}
        )
        
        self.feedback_items.append(feedback)
        self._trigger_hooks(feedback)
        
        return feedback_id
    
    def register_feedback_hook(self, event_type: str, callback: callable) -> None:
        """Register a callback for feedback events."""
        if event_type not in self.feedback_hooks:
            self.feedback_hooks[event_type] = []
        self.feedback_hooks[event_type].append(callback)
    
    def _trigger_hooks(self, feedback: Feedback) -> None:
        """Trigger registered hooks for new feedback."""
        # Trigger general feedback hooks
        for callback in self.feedback_hooks.get("feedback_received", []):
            try:
                callback(feedback)
            except Exception as e:
                print(f"Error in feedback hook: {e}")
        
        # Trigger specific type hooks
        hook_name = f"feedback_{feedback.feedback_type.value}"
        for callback in self.feedback_hooks.get(hook_name, []):
            try:
                callback(feedback)
            except Exception as e:
                print(f"Error in feedback hook {hook_name}: {e}")
    
    def get_feedback_for_target(
        self,
        target_type: str,
        target_id: str,
        feedback_type: Optional[FeedbackType] = None,
        source: Optional[FeedbackSource] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Feedback]:
        """Get feedback for a specific target."""
        filtered_feedback = []
        
        for feedback in self.feedback_items:
            # Filter by target
            if feedback.target_type != target_type or feedback.target_id != target_id:
                continue
            
            # Filter by feedback type
            if feedback_type and feedback.feedback_type != feedback_type:
                continue
            
            # Filter by source
            if source and feedback.source != source:
                continue
            
            # Filter by time range
            if start_time and feedback.timestamp < start_time:
                continue
            
            if end_time and feedback.timestamp > end_time:
                continue
            
            filtered_feedback.append(feedback)
        
        return filtered_feedback
    
    def get_feedback_summary(
        self,
        target_type: str,
        target_id: str,
        feedback_type: Optional[FeedbackType] = None
    ) -> Dict[str, Any]:
        """Get a summary of feedback for a target."""
        feedback_items = self.get_feedback_for_target(target_type, target_id, feedback_type)
        
        if not feedback_items:
            return {
                "target_type": target_type,
                "target_id": target_id,
                "total_feedback": 0,
                "status": "no_feedback"
            }
        
        ratings = [f.rating for f in feedback_items if f.rating is not None]
        
        summary = {
            "target_type": target_type,
            "target_id": target_id,
            "total_feedback": len(feedback_items),
            "feedback_by_type": {},
            "feedback_by_source": {},
            "time_range": {
                "earliest": min(f.timestamp for f in feedback_items).isoformat(),
                "latest": max(f.timestamp for f in feedback_items).isoformat()
            }
        }
        
        # Count by type
        for feedback in feedback_items:
            feedback_type_str = feedback.feedback_type.value
            summary["feedback_by_type"][feedback_type_str] = \
                summary["feedback_by_type"].get(feedback_type_str, 0) + 1
        
        # Count by source
        for feedback in feedback_items:
            source_str = feedback.source.value
            summary["feedback_by_source"][source_str] = \
                summary["feedback_by_source"].get(source_str, 0) + 1
        
        # Rating statistics
        if ratings:
            summary["rating_stats"] = {
                "count": len(ratings),
                "average": sum(ratings) / len(ratings),
                "min": min(ratings),
                "max": max(ratings)
            }
        
        return summary
    
    def clear_old_feedback(self, before_time: datetime) -> int:
        """Clear feedback older than specified time."""
        original_count = len(self.feedback_items)
        self.feedback_items = [f for f in self.feedback_items if f.timestamp >= before_time]
        return original_count - len(self.feedback_items)