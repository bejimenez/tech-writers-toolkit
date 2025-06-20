# src/agents/technical_agent.py
"""Technical accuracy review agent for installation instructions"""

import re
from typing import List, Optional
from src.agents.base_agent import BaseReviewAgent, ReviewContext
from src.storage.models import AgentFinding
from src.ai.prompts import PromptTemplates
from src.ai.llm_provider import LLMManager
from src.utils.config import Config


class TechnicalAgent(BaseReviewAgent):
    """
    Technical accuracy review agent that focuses on:
    - Technical errors and inconsistencies
    - Safety warnings and procedures
    - Completeness of instructions
    - Tool requirements
    - Troubleshooting guidance
    """
    
    def __init__(self):
        super().__init__(
            role="Technical Accuracy Reviewer",
            goal="Identify technical errors, safety issues, and completeness problems in installation instructions",
            backstory="You are an experienced field technician with 15+ years installing access control hardware. You've seen every mistake that can cause installation failures, safety issues, or damage to equipment. Your expertise helps ensure that installation instructions are technically accurate and complete.",
            confidence_threshold=0.6
        )
        
        # Initialize LLM manager if available
        self.llm_manager = None
        if Config.GROQ_API_KEY or Config.GEMINI_API_KEY:
            try:
                self.llm_manager = LLMManager()
                self.logger.info("LLM Manager initialized for Technical Agent")
            except Exception as e:
                self.logger.warning("Failed to initialize LLM Manager for Technical Agent", error=str(e))
    
    def review(self, context: ReviewContext) -> List[AgentFinding]:
        """
        Perform technical accuracy review of the document
        
        Args:
            context: Review context with document and session info
            
        Returns:
            List of technical findings
        """
        findings = []
        
        # If LLM is available, use AI-powered review
        if self.llm_manager:
            ai_findings = self._perform_ai_review(context)
            findings.extend(ai_findings)
        
        # Always perform rule-based review as fallback/supplement
        rule_findings = self._perform_rule_based_review(context)
        findings.extend(rule_findings)
        
        self.logger.info(
            "Technical review completed",
            session_id=context.session_id,
            ai_findings=len(ai_findings) if self.llm_manager else 0,
            rule_findings=len(rule_findings),
            total_findings=len(findings)
        )
        
        return findings
    
    def _perform_ai_review(self, context: ReviewContext) -> List[AgentFinding]:
        """Perform AI-powered technical review"""
        findings = []

        if not self.llm_manager:
            self.logger.warning(
                "LLM Manager is not initialized; skipping AI technical review",
                session_id=context.session_id
            )
            return findings
        try:
            # Get technical review prompt
            prompt = PromptTemplates.get_agent_prompt("technical", context.document_text)
            
            # Generate AI response
            response = self.llm_manager.generate_response(
                prompt,
                max_tokens=Config.MAX_TOKENS_PER_REQUEST,
                temperature=0.3  # Lower temperature for more consistent technical analysis
            )
            
            # Parse AI response into findings
            ai_findings = self._parse_ai_response(response, context.session_id)
            findings.extend(ai_findings)
            
            self.logger.info(
                "AI technical review completed",
                session_id=context.session_id,
                findings_count=len(ai_findings)
            )
            
        except Exception as e:
            self.logger.error(
                "AI technical review failed",
                session_id=context.session_id,
                error=str(e)
            )
            # Continue with rule-based review even if AI fails
        
        return findings
    
    def _parse_ai_response(self, response: str, session_id: int) -> List[AgentFinding]:
        """Parse AI response into structured findings"""
        findings = []
        
        try:
            # Look for the FINDINGS section
            if "FINDINGS:" in response:
                findings_section = response.split("FINDINGS:")[1].strip()
            else:
                findings_section = response
            
            # Split by "---" or double newlines to separate findings
            raw_findings = re.split(r'---+|\n\n\n+', findings_section)
            
            for raw_finding in raw_findings:
                finding = self._parse_single_finding(raw_finding.strip(), session_id)
                if finding:
                    findings.append(finding)
            
        except Exception as e:
            self.logger.error("Failed to parse AI response", error=str(e), response=response[:200])
        
        return findings
    
    def _parse_single_finding(self, raw_finding: str, session_id: int) -> Optional[AgentFinding]:
        """Parse a single finding from AI response"""
        if not raw_finding or len(raw_finding) < 10:
            return None
        
        try:
            lines = raw_finding.split('\n')
            
            # Look for pattern: [Severity] - [Location]: [Description]
            main_line = lines[0] if lines else ""
            
            # Extract severity
            severity_match = re.match(r'\[(\w+)\]\s*-\s*(.+)', main_line)
            if not severity_match:
                # Try alternative format: "Error - Location: Description"
                severity_match = re.match(r'(\w+)\s*-\s*(.+)', main_line)
            
            if not severity_match:
                # If no clear format, default to warning
                severity = "warning"
                location = "Document"
                description = raw_finding
            else:
                severity = severity_match.group(1).lower()
                rest = severity_match.group(2)
                
                # Extract location and description
                if ':' in rest:
                    location, description = rest.split(':', 1)
                    location = location.strip()
                    description = description.strip()
                else:
                    location = "Document"
                    description = rest.strip()
            
            # Look for suggestion in subsequent lines
            suggestion = None
            for line in lines[1:]:
                if line.strip().lower().startswith('suggestion:'):
                    suggestion = line.split(':', 1)[1].strip()
                    break
            
            # Validate severity
            if severity not in ['error', 'warning', 'info']:
                severity = 'warning'
            
            # Create finding
            return self.create_finding(
                session_id=session_id,
                severity=severity,
                category="technical",
                description=description,
                location=location,
                suggestion=suggestion,
                confidence=0.8  # AI findings get high confidence
            )
            
        except Exception as e:
            self.logger.error("Failed to parse single finding", error=str(e), raw_finding=raw_finding[:100])
            return None
    
    def _perform_rule_based_review(self, context: ReviewContext) -> List[AgentFinding]:
        """Perform rule-based technical review as fallback/supplement"""
        findings = []
        text = context.document_text.lower()
        
        # Check for common technical issues
        findings.extend(self._check_safety_warnings(text, context.session_id))
        findings.extend(self._check_tool_requirements(text, context.session_id))
        findings.extend(self._check_measurement_issues(text, context.session_id))
        findings.extend(self._check_sequence_issues(text, context.session_id))
        
        return findings
    
    def _check_safety_warnings(self, text: str, session_id: int) -> List[AgentFinding]:
        """Check for adequate safety warnings"""
        findings = []
        
        # Look for electrical work without safety warnings
        electrical_terms = ['wire', 'wiring', 'electrical', 'power', 'voltage', 'connect power']
        safety_terms = ['danger', 'warning', 'caution', 'safety', 'turn off power', 'disconnect power']
        
        has_electrical = any(term in text for term in electrical_terms)
        has_safety = any(term in text for term in safety_terms)
        
        if has_electrical and not has_safety:
            findings.append(self.create_finding(
                session_id=session_id,
                severity="warning",
                category="safety",
                description="Document contains electrical procedures but lacks adequate safety warnings",
                location="Throughout document",
                suggestion="Add safety warnings about turning off power before electrical work",
                confidence=0.9
            ))
        
        return findings
    
    def _check_tool_requirements(self, text: str, session_id: int) -> List[AgentFinding]:
        """Check for missing tool requirements"""
        findings = []
        
        # Look for installation steps without tool specifications
        action_terms = ['drill', 'screw', 'cut', 'strip', 'connect', 'mount', 'install']
        tool_terms = ['screwdriver', 'drill bit', 'wire stripper', 'multimeter', 'level']
        
        has_actions = any(term in text for term in action_terms)
        has_tools = any(term in text for term in tool_terms)
        
        if has_actions and not has_tools:
            findings.append(self.create_finding(
                session_id=session_id,
                severity="warning",
                category="tools",
                description="Installation procedures mentioned without specifying required tools",
                location="Installation steps",
                suggestion="Add a tools and materials list at the beginning of the document",
                confidence=0.7
            ))
        
        return findings
    
    def _check_measurement_issues(self, text: str, session_id: int) -> List[AgentFinding]:
        """Check for measurement and specification issues"""
        findings = []
        
        # Look for measurements without units
        measurement_pattern = r'\b\d+\.?\d*\s*(?!mm|cm|inch|in\b|ft\b|meter|gauge|awg)'
        matches = re.findall(measurement_pattern, text)
        
        if len(matches) > 3:  # Multiple measurements without units
            findings.append(self.create_finding(
                session_id=session_id,
                severity="warning",
                category="measurements",
                description="Multiple measurements found without units specified",
                location="Throughout document",
                suggestion="Ensure all measurements include appropriate units (mm, inches, etc.)",
                confidence=0.6
            ))
        
        return findings
    
    def _check_sequence_issues(self, text: str, session_id: int) -> List[AgentFinding]:
        """Check for logical sequence issues in instructions"""
        findings = []
        
        # Look for power connection before other steps (potentially dangerous)
        power_early = False
        if 'connect power' in text or 'plug in' in text:
            text_parts = text.split('.')
            for i, part in enumerate(text_parts[:3]):  # Check first few sentences
                if 'connect power' in part or 'plug in' in part:
                    power_early = True
                    break
        
        if power_early:
            findings.append(self.create_finding(
                session_id=session_id,
                severity="error",
                category="sequence",
                description="Power connection appears early in instructions - potential safety hazard",
                location="Installation sequence",
                suggestion="Move power connection to the final step after all other connections are complete",
                confidence=0.8
            ))
        
        return findings