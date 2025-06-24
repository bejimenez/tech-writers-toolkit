# src/ai/agent_manager.py
"""Agent manager for coordinating document reviews"""

import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.utils.logger import LoggerMixin
from src.agents.base_agent import ReviewContext
from src.agents.technical_agent import TechnicalAgent
from src.agents.diagram_agent import DiagramAgent
from src.storage.models import AgentFinding, DatabaseManager
from src.document.processor import ProcessedContent


@dataclass
class ReviewResult:
    """Result of a complete review process"""
    session_id: int
    findings: List[AgentFinding]
    agent_results: Dict[str, List[AgentFinding]]
    total_processing_time: float
    status: str  # "completed", "partial", "failed"
    summary: Optional[str] = None


class AgentManager(LoggerMixin):
    """Manages AI agents and coordinates document reviews"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.agents = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize available review agents"""
        try:
            # Initialize Technical Agent
            self.agents["technical"] = TechnicalAgent()
            self.logger.info("Technical Agent initialized")
            self.agents["diagram"] = DiagramAgent()
            self.logger.info("Diagram Agent initialized")
            
        except Exception as e:
            self.logger.error("Failed to initialize agents", error=str(e))
    
    def start_review(
        self, 
        processed_content: ProcessedContent,
        agents_to_use: Optional[List[str]] = None
    ) -> ReviewResult:
        """
        Start a complete review process using specified agents
        
        Args:
            processed_content: The processed document content
            agents_to_use: List of agent names to use (default: all available)
            
        Returns:
            ReviewResult with findings from all agents
        """
        start_time = time.time()
        session_id = processed_content.session_id
        
        if not session_id:
            raise ValueError("ProcessedContent must have a session_id")
        
        self.logger.info(
            "Starting agent review",
            session_id=session_id,
            document=processed_content.document_info.filename,
            agents_requested=agents_to_use or list(self.agents.keys())
        )
        
        # Determine which agents to use
        if agents_to_use is None:
            agents_to_use = list(self.agents.keys())
        
        # Create review context
        context = ReviewContext(
            document_text=processed_content.text,
            document_info={
                "filename": processed_content.document_info.filename,
                "page_count": processed_content.document_info.page_count,
                "processing_method": processed_content.document_info.processing_method,
                "has_images": processed_content.document_info.has_images
            },
            session_id=session_id
        )
        
        # Run agents and collect results
        all_findings = []
        agent_results = {}
        successful_agents = 0
        
        for agent_name in agents_to_use:
            if agent_name not in self.agents:
                self.logger.warning("Unknown agent requested", agent=agent_name)
                continue
            
            try:
                agent = self.agents[agent_name]
                agent_findings = agent.execute_review(context)
                
                # Store findings in database
                for finding in agent_findings:
                    finding_id = self.db_manager.add_agent_finding(finding)
                    finding.id = finding_id
                
                agent_results[agent_name] = agent_findings
                all_findings.extend(agent_findings)
                successful_agents += 1
                
                self.logger.info(
                    "Agent completed review",
                    agent=agent_name,
                    session_id=session_id,
                    findings_count=len(agent_findings)
                )
                
            except Exception as e:
                self.logger.error(
                    "Agent review failed",
                    agent=agent_name,
                    session_id=session_id,
                    error=str(e)
                )
                agent_results[agent_name] = []
        
        # Determine overall status
        total_time = time.time() - start_time
        
        if successful_agents == 0:
            status = "failed"
        elif successful_agents < len(agents_to_use):
            status = "partial"
        else:
            status = "completed"
        
        # Create summary
        summary = self._create_review_summary(all_findings, agent_results, status)
        
        result = ReviewResult(
            session_id=session_id,
            findings=all_findings,
            agent_results=agent_results,
            total_processing_time=total_time,
            status=status,
            summary=summary
        )
        
        self.logger.info(
            "Agent review completed",
            session_id=session_id,
            status=status,
            total_findings=len(all_findings),
            agents_used=successful_agents,
            processing_time=f"{total_time:.2f}s"
        )
        
        return result
    
    def _create_review_summary(
        self, 
        findings: List[AgentFinding], 
        agent_results: Dict[str, List[AgentFinding]],
        status: str
    ) -> str:
        """Create a human-readable summary of the review"""
        
        if not findings:
            return "No issues found in the document. The content appears to be technically sound."
        
        # Count findings by severity
        severity_counts = {"error": 0, "warning": 0, "info": 0}
        for finding in findings:
            severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
        
        # Create summary text
        summary_parts = []
        
        if severity_counts["error"] > 0:
            summary_parts.append(f"{severity_counts['error']} critical issue(s) that must be fixed")
        
        if severity_counts["warning"] > 0:
            summary_parts.append(f"{severity_counts['warning']} warning(s) that should be addressed")
        
        if severity_counts["info"] > 0:
            summary_parts.append(f"{severity_counts['info']} suggestion(s) for improvement")
        
        if summary_parts:
            summary = f"Review found: {', '.join(summary_parts)}."
        else:
            summary = "Review completed with mixed results."
        
        # Add agent-specific information
        agent_info = []
        for agent_name, agent_findings in agent_results.items():
            if agent_findings:
                agent_info.append(f"{agent_name}: {len(agent_findings)} findings")
        
        if agent_info:
            summary += f" Agent breakdown: {', '.join(agent_info)}."
        
        # Add status information
        if status == "partial":
            summary += " Note: Some agents failed to complete their review."
        elif status == "failed":
            summary = "Review failed - unable to complete analysis."
        
        return summary
    
    def get_review_by_session(self, session_id: int) -> Optional[ReviewResult]:
        """Get review results for a specific session"""
        try:
            # Get findings from database
            findings = self.db_manager.get_session_findings(session_id)
            
            if not findings:
                return None
            
            # Group findings by agent
            agent_results = {}
            for finding in findings:
                agent_name = finding.agent_name
                if agent_name not in agent_results:
                    agent_results[agent_name] = []
                agent_results[agent_name].append(finding)
            
            # Create summary
            summary = self._create_review_summary(findings, agent_results, "completed")
            
            return ReviewResult(
                session_id=session_id,
                findings=findings,
                agent_results=agent_results,
                total_processing_time=0.0,  # Not stored
                status="completed",
                summary=summary
            )
            
        except Exception as e:
            self.logger.error("Failed to get review by session", session_id=session_id, error=str(e))
            return None
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agent names"""
        return list(self.agents.keys())
    
    def test_agents(self) -> Dict[str, bool]:
        """Test all agents to see if they're working"""
        results = {}
        
        # Create a simple test context
        test_context = ReviewContext(
            document_text="This is a test document for agent validation.",
            document_info={"filename": "test.txt", "page_count": 1},
            session_id=0  # Test session
        )
        
        for agent_name, agent in self.agents.items():
            try:
                # Try to run the agent
                findings = agent.review(test_context)
                results[agent_name] = True
                self.logger.info(f"Agent {agent_name} test passed")
                
            except Exception as e:
                results[agent_name] = False
                self.logger.error(f"Agent {agent_name} test failed", error=str(e))
        
        return results