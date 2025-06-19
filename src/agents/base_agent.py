# src/agents/base_agent.py
"""Base agent class for all review agents"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time

from src.utils.logger import LoggerMixin
from src.storage.models import AgentFinding

@dataclass
class ReviewContext:
    """Context information for agent review"""
    document_text: str
    document_info: Dict[str, Any]
    session_id: int
    user_preferences: Optional[Dict[str, Any]] = None
    previous_findings: Optional[List[AgentFinding]] = None

class BaseReviewAgent(ABC, LoggerMixin):
    """
    Base class for all review agents in the system.
    
    This class provides the foundation for specialized review agetns that examine different aspects of technical documents."""

    def __init__(
            self,
            role: str,
            goal: str,
            backstory: str,
            confidence_threshold: float = 0.7,
    ):
        """
        Initialize the base agent with role, goal, and backstory, confidence_threshold, and empty findings:
        
        Args:
            role: The role of the agent (e.g., "Technical Reviewer")
            goal: The primary goal of the agent (e.g., "Identify technical issues")
            backstory: Background information to provide context
            confidence_threshold: Minimum confidence level for findings
        """
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.confidence_threshold = confidence_threshold
        self.findings: List[AgentFinding] = []
        self.logger.info(f"Initialized {self.__class__.__name__} agent", role=self.role, goal=self.goal)

    @abstractmethod
    def review(self, context: ReviewContext) -> List[AgentFinding]:
        """
        Analyze document content and return findings.
        
        Args:
            context: review context with document and sesison info
            
        Returns:
            List of AgentFinding objects with identified issues
        
        Raises:
            ReviewException: If review fails for any reason
        """
        raise NotImplementedError("Subclasses must implement the review method review()")
    
    def execute_review(self, context: ReviewContext) -> List[AgentFinding]:
        """
        Execute the review with timing and error handling.
        
        Args:
            context: review context
        
        Returns:
            List of findings from this agent
        """
        start_time = time.time()

        self.logger.info(
            "Starting agent review",
            agent=self.role,
            session_id=context.session_id,
            document_length=len(context.document_text),
        )

        try:
            findings = self.review(context)

            # Filter findings based on confidence threshold
            filtered_findings = [
                f for f in findings
                if f.confidence >= self.confidence_threshold
            ]

            execution_time = time.time() - start_time

            self.logger.info(
                "Agent review completed",
                agent=self.role,
                session_id=context.session_id,
                findings_count=len(filtered_findings),
                execution_time=f"{execution_time:.2f}s"
            )

            return filtered_findings
        
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(
                "Agent review failed",
                agent=self.role,
                session_id=context.session_id,
                error=str(e),
                execution_time=f"{execution_time:.2f}s"
            )

            # Return empty findings on failure
            return []
        
    def create_finding(
            self,
            session_id: int,
            severity: str,
            category: str,
            description: str,
            location: str,
            suggestion: Optional[str] = None,
            confidence: float = 1.0
    ) -> AgentFinding:
        """
        Create a new AgentFinding object with the provided details.
        
        Args:
            session_id: Review session ID
            severity: error, warning, or info
            category: Type of issue (formatting, technical, etc.)
            description: Human-readable description
            location: Where in document this was found
            suggestion: Optional fix suggestion
            confidence: Confidence level (0.0 to 1.0)
            
        Returns:
            AgentFinding object
        """
        return AgentFinding(
            session_id=session_id,
            agent_name=self.role,
            severity=severity,
            category=category,
            description=description,
            location=location,
            suggestion=suggestion,
            confidence=confidence
        )

class ReviewException(Exception):
    """Exception raised during review process"""
    pass