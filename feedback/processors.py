"""
Feedback processing and analysis.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from .collectors import Feedback, FeedbackType, FeedbackSource, FeedbackCollector


class FeedbackProcessor:
    """Processes and analyzes feedback data."""
    
    def __init__(self, feedback_collector: FeedbackCollector):
        """Initialize feedback processor."""
        self.feedback_collector = feedback_collector
        self.improvement_suggestions: List[Dict[str, Any]] = []
    
    def analyze_agent_feedback(self, agent_id: str, days: int = 7) -> Dict[str, Any]:
        """Analyze feedback for a specific agent."""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        feedback_items = self.feedback_collector.get_feedback_for_target(
            "agent", agent_id, start_time=start_time, end_time=end_time
        )
        
        if not feedback_items:
            return {
                "agent_id": agent_id,
                "analysis_period": f"{days} days",
                "status": "no_feedback",
                "feedback_count": 0
            }
        
        analysis = {
            "agent_id": agent_id,
            "analysis_period": f"{days} days",
            "feedback_count": len(feedback_items),
            "performance_trends": self._analyze_performance_trends(feedback_items),
            "sentiment_analysis": self._analyze_sentiment(feedback_items),
            "improvement_areas": self._identify_improvement_areas(feedback_items),
            "positive_aspects": self._identify_positive_aspects(feedback_items),
            "recommendations": self._generate_agent_recommendations(feedback_items)
        }
        
        return analysis
    
    def analyze_campaign_feedback(self, campaign_name: str) -> Dict[str, Any]:
        """Analyze feedback for a campaign."""
        feedback_items = self.feedback_collector.get_feedback_for_target("campaign", campaign_name)
        
        if not feedback_items:
            return {
                "campaign": campaign_name,
                "status": "no_feedback",
                "feedback_count": 0
            }
        
        return {
            "campaign": campaign_name,
            "feedback_count": len(feedback_items),
            "user_satisfaction": self._calculate_user_satisfaction(feedback_items),
            "common_issues": self._identify_common_issues(feedback_items),
            "success_factors": self._identify_success_factors(feedback_items),
            "recommendations": self._generate_campaign_recommendations(feedback_items)
        }
    
    def process_real_time_feedback(self, feedback: Feedback) -> Dict[str, Any]:
        """Process feedback in real-time and generate immediate insights."""
        processing_result = {
            "feedback_id": feedback.feedback_id,
            "processed_at": datetime.now().isoformat(),
            "immediate_actions": [],
            "alerts": [],
            "priority": "normal"
        }
        
        # Check for critical issues
        if feedback.feedback_type == FeedbackType.ERROR_REPORT:
            processing_result["priority"] = "high"
            processing_result["alerts"].append("Error reported - requires immediate attention")
            processing_result["immediate_actions"].append("Investigate error and implement fix")
        
        # Check for very low ratings
        if feedback.rating is not None and feedback.rating < 2.0:
            processing_result["priority"] = "high"
            processing_result["alerts"].append("Very low rating received")
            processing_result["immediate_actions"].append("Review performance and identify issues")
        
        # Check for repeated issues
        similar_feedback = self._find_similar_feedback(feedback)
        if len(similar_feedback) > 3:
            processing_result["alerts"].append("Repeated similar feedback detected")
            processing_result["immediate_actions"].append("Address recurring issue")
        
        return processing_result
    
    def generate_improvement_plan(self, target_type: str, target_id: str) -> Dict[str, Any]:
        """Generate an improvement plan based on feedback analysis."""
        feedback_items = self.feedback_collector.get_feedback_for_target(target_type, target_id)
        
        if not feedback_items:
            return {
                "target_type": target_type,
                "target_id": target_id,
                "status": "no_feedback_available"
            }
        
        # Analyze patterns and issues
        issues = self._identify_recurring_issues(feedback_items)
        strengths = self._identify_strengths(feedback_items)
        
        improvement_plan = {
            "target_type": target_type,
            "target_id": target_id,
            "generated_at": datetime.now().isoformat(),
            "current_status": self._assess_current_status(feedback_items),
            "identified_issues": issues,
            "identified_strengths": strengths,
            "improvement_actions": self._generate_improvement_actions(issues),
            "timeline": self._estimate_improvement_timeline(issues),
            "success_metrics": self._define_success_metrics(target_type, issues)
        }
        
        return improvement_plan
    
    def _analyze_performance_trends(self, feedback_items: List[Feedback]) -> Dict[str, Any]:
        """Analyze performance trends from feedback."""
        performance_feedback = [f for f in feedback_items if f.feedback_type == FeedbackType.PERFORMANCE]
        
        if not performance_feedback:
            return {"status": "no_performance_feedback"}
        
        # Sort by timestamp
        performance_feedback.sort(key=lambda x: x.timestamp)
        
        ratings = [f.rating for f in performance_feedback if f.rating is not None]
        
        if len(ratings) < 2:
            return {"status": "insufficient_data"}
        
        # Calculate trend
        early_ratings = ratings[:len(ratings)//2]
        recent_ratings = ratings[len(ratings)//2:]
        
        early_avg = sum(early_ratings) / len(early_ratings)
        recent_avg = sum(recent_ratings) / len(recent_ratings)
        
        trend = "improving" if recent_avg > early_avg else "declining" if recent_avg < early_avg else "stable"
        
        return {
            "trend": trend,
            "early_average": early_avg,
            "recent_average": recent_avg,
            "change": recent_avg - early_avg,
            "total_feedback": len(performance_feedback)
        }
    
    def _analyze_sentiment(self, feedback_items: List[Feedback]) -> Dict[str, Any]:
        """Analyze sentiment from feedback comments."""
        comments = [f.comment for f in feedback_items if f.comment]
        
        if not comments:
            return {"status": "no_comments"}
        
        # Simple sentiment analysis based on keywords
        positive_keywords = ["good", "great", "excellent", "helpful", "fast", "accurate", "impressive"]
        negative_keywords = ["bad", "poor", "slow", "error", "problem", "issue", "failed", "disappointing"]
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for comment in comments:
            comment_lower = comment.lower()
            has_positive = any(keyword in comment_lower for keyword in positive_keywords)
            has_negative = any(keyword in comment_lower for keyword in negative_keywords)
            
            if has_positive and not has_negative:
                positive_count += 1
            elif has_negative and not has_positive:
                negative_count += 1
            else:
                neutral_count += 1
        
        total = len(comments)
        
        return {
            "total_comments": total,
            "positive": positive_count,
            "negative": negative_count,
            "neutral": neutral_count,
            "sentiment_score": (positive_count - negative_count) / total if total > 0 else 0
        }
    
    def _identify_improvement_areas(self, feedback_items: List[Feedback]) -> List[str]:
        """Identify areas that need improvement."""
        improvement_areas = []
        
        # Check for low ratings
        low_rating_feedback = [f for f in feedback_items if f.rating is not None and f.rating < 3.0]
        if len(low_rating_feedback) > len(feedback_items) * 0.3:
            improvement_areas.append("Overall performance quality")
        
        # Check for error reports
        error_feedback = [f for f in feedback_items if f.feedback_type == FeedbackType.ERROR_REPORT]
        if error_feedback:
            improvement_areas.append("Error handling and reliability")
        
        # Check comments for common issues
        comments = [f.comment for f in feedback_items if f.comment]
        common_issues = self._extract_common_issues(comments)
        improvement_areas.extend(common_issues)
        
        return list(set(improvement_areas))
    
    def _identify_positive_aspects(self, feedback_items: List[Feedback]) -> List[str]:
        """Identify positive aspects from feedback."""
        positive_aspects = []
        
        # Check for high ratings
        high_rating_feedback = [f for f in feedback_items if f.rating is not None and f.rating >= 4.0]
        if len(high_rating_feedback) > len(feedback_items) * 0.6:
            positive_aspects.append("Strong overall performance")
        
        # Extract positive mentions from comments
        comments = [f.comment for f in feedback_items if f.comment]
        positive_mentions = self._extract_positive_mentions(comments)
        positive_aspects.extend(positive_mentions)
        
        return list(set(positive_aspects))
    
    def _generate_agent_recommendations(self, feedback_items: List[Feedback]) -> List[str]:
        """Generate recommendations for agent improvement."""
        recommendations = []
        
        improvement_areas = self._identify_improvement_areas(feedback_items)
        
        for area in improvement_areas:
            if "performance" in area.lower():
                recommendations.append("Consider optimizing agent algorithms for better performance")
            elif "error" in area.lower():
                recommendations.append("Implement better error handling and validation")
            elif "response" in area.lower() or "speed" in area.lower():
                recommendations.append("Optimize response time and processing speed")
        
        # Check rating trends
        ratings = [f.rating for f in feedback_items if f.rating is not None]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            if avg_rating < 3.0:
                recommendations.append("Overall performance needs significant improvement")
            elif avg_rating < 4.0:
                recommendations.append("Focus on consistency and reliability improvements")
        
        return recommendations or ["Continue current performance level"]
    
    def _calculate_user_satisfaction(self, feedback_items: List[Feedback]) -> Dict[str, Any]:
        """Calculate user satisfaction metrics."""
        satisfaction_feedback = [
            f for f in feedback_items 
            if f.feedback_type == FeedbackType.USER_SATISFACTION and f.rating is not None
        ]
        
        if not satisfaction_feedback:
            return {"status": "no_satisfaction_data"}
        
        ratings = [f.rating for f in satisfaction_feedback]
        
        return {
            "total_responses": len(ratings),
            "average_rating": sum(ratings) / len(ratings),
            "satisfaction_distribution": {
                "very_satisfied": len([r for r in ratings if r >= 4.5]),
                "satisfied": len([r for r in ratings if 3.5 <= r < 4.5]),
                "neutral": len([r for r in ratings if 2.5 <= r < 3.5]),
                "dissatisfied": len([r for r in ratings if 1.5 <= r < 2.5]),
                "very_dissatisfied": len([r for r in ratings if r < 1.5])
            }
        }
    
    def _identify_common_issues(self, feedback_items: List[Feedback]) -> List[str]:
        """Identify common issues from feedback."""
        error_feedback = [f for f in feedback_items if f.feedback_type == FeedbackType.ERROR_REPORT]
        comments = [f.comment for f in feedback_items if f.comment]
        
        issues = []
        
        # Analyze error patterns
        if len(error_feedback) > 2:
            issues.append("Recurring errors detected")
        
        # Analyze comment patterns
        issues.extend(self._extract_common_issues(comments))
        
        return list(set(issues))
    
    def _extract_common_issues(self, comments: List[str]) -> List[str]:
        """Extract common issues from comment text."""
        issues = []
        issue_keywords = {
            "slow": "Response time issues",
            "error": "Error occurrences", 
            "fail": "Task failures",
            "confus": "User confusion",
            "difficult": "Usability issues"
        }
        
        for comment in comments:
            comment_lower = comment.lower()
            for keyword, issue in issue_keywords.items():
                if keyword in comment_lower and issue not in issues:
                    issues.append(issue)
        
        return issues
    
    def _extract_positive_mentions(self, comments: List[str]) -> List[str]:
        """Extract positive mentions from comments."""
        positive_aspects = []
        positive_keywords = {
            "fast": "Good response time",
            "accurate": "High accuracy",
            "helpful": "Helpful responses", 
            "easy": "User-friendly",
            "reliable": "Reliable performance"
        }
        
        for comment in comments:
            comment_lower = comment.lower()
            for keyword, aspect in positive_keywords.items():
                if keyword in comment_lower and aspect not in positive_aspects:
                    positive_aspects.append(aspect)
        
        return positive_aspects
    
    def _find_similar_feedback(self, feedback: Feedback) -> List[Feedback]:
        """Find feedback similar to the given feedback."""
        all_feedback = self.feedback_collector.feedback_items
        
        similar = []
        for item in all_feedback:
            if (item.target_type == feedback.target_type and 
                item.target_id == feedback.target_id and
                item.feedback_type == feedback.feedback_type and
                item.feedback_id != feedback.feedback_id):
                similar.append(item)
        
        return similar
    
    def _identify_recurring_issues(self, feedback_items: List[Feedback]) -> List[Dict[str, Any]]:
        """Identify recurring issues from feedback."""
        issue_patterns = {}
        
        for feedback in feedback_items:
            if feedback.feedback_type == FeedbackType.ERROR_REPORT:
                error_type = feedback.metadata.get("error_type", "unknown")
                if error_type not in issue_patterns:
                    issue_patterns[error_type] = []
                issue_patterns[error_type].append(feedback)
        
        recurring_issues = []
        for issue_type, instances in issue_patterns.items():
            if len(instances) > 2:
                recurring_issues.append({
                    "issue_type": issue_type,
                    "occurrences": len(instances),
                    "severity": "high" if len(instances) > 5 else "medium",
                    "first_occurrence": min(f.timestamp for f in instances).isoformat(),
                    "last_occurrence": max(f.timestamp for f in instances).isoformat()
                })
        
        return recurring_issues
    
    def _identify_strengths(self, feedback_items: List[Feedback]) -> List[str]:
        """Identify strengths from feedback."""
        return self._identify_positive_aspects(feedback_items)
    
    def _generate_improvement_actions(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate specific improvement actions."""
        actions = []
        
        for issue in issues:
            issue_type = issue.get("issue_type", "unknown")
            severity = issue.get("severity", "medium")
            
            action = {
                "action_id": f"fix_{issue_type}_{datetime.now().strftime('%Y%m%d')}",
                "description": f"Address {issue_type} issues",
                "priority": severity,
                "estimated_effort": "medium",
                "target_completion": "2 weeks"
            }
            
            actions.append(action)
        
        return actions
    
    def _estimate_improvement_timeline(self, issues: List[Dict[str, Any]]) -> Dict[str, str]:
        """Estimate timeline for improvements."""
        if not issues:
            return {"status": "no_issues_identified"}
        
        high_priority_issues = [i for i in issues if i.get("severity") == "high"]
        medium_priority_issues = [i for i in issues if i.get("severity") == "medium"]
        
        timeline = {}
        
        if high_priority_issues:
            timeline["immediate"] = f"{len(high_priority_issues)} high priority issues"
        
        if medium_priority_issues:
            timeline["short_term"] = f"{len(medium_priority_issues)} medium priority issues"
        
        timeline["estimated_completion"] = "4-6 weeks"
        
        return timeline
    
    def _define_success_metrics(self, target_type: str, issues: List[Dict[str, Any]]) -> List[str]:
        """Define success metrics for improvement plan."""
        metrics = [
            "Increase average rating to >4.0",
            "Reduce error rate by 50%",
            "Achieve 90% user satisfaction"
        ]
        
        if target_type == "agent":
            metrics.append("Improve task completion rate to >95%")
            metrics.append("Reduce average response time by 20%")
        
        return metrics
    
    def _assess_current_status(self, feedback_items: List[Feedback]) -> Dict[str, Any]:
        """Assess current status based on feedback."""
        ratings = [f.rating for f in feedback_items if f.rating is not None]
        error_count = len([f for f in feedback_items if f.feedback_type == FeedbackType.ERROR_REPORT])
        
        status = {
            "overall_health": "good",
            "total_feedback": len(feedback_items),
            "error_reports": error_count
        }
        
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            status["average_rating"] = avg_rating
            
            if avg_rating < 2.5:
                status["overall_health"] = "poor"
            elif avg_rating < 3.5:
                status["overall_health"] = "fair"
            elif avg_rating >= 4.0:
                status["overall_health"] = "excellent"
        
        if error_count > len(feedback_items) * 0.2:
            status["overall_health"] = "poor"
        
        return status
    
    def _identify_success_factors(self, feedback_items: List[Feedback]) -> List[str]:
        """Identify factors contributing to success."""
        return self._identify_positive_aspects(feedback_items)
    
    def _generate_campaign_recommendations(self, feedback_items: List[Feedback]) -> List[str]:
        """Generate campaign-specific recommendations."""
        recommendations = []
        
        satisfaction = self._calculate_user_satisfaction(feedback_items)
        if satisfaction.get("status") != "no_satisfaction_data":
            avg_rating = satisfaction.get("average_rating", 0)
            if avg_rating < 3.5:
                recommendations.append("Review campaign objectives and execution strategy")
        
        common_issues = self._identify_common_issues(feedback_items)
        if common_issues:
            recommendations.append("Address identified common issues")
        
        return recommendations or ["Campaign is performing well"]