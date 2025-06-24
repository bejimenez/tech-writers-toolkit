# src/agents/diagram_agent.py
"""Diagram and visual review agent for wiring diagrams."""

import re
import base64
import io
from typing import List, Optional, Dict, Any
from PIL import Image

from src.agents.base_agent import BaseReviewAgent, ReviewContext
from src.storage.models import AgentFinding
from src.ai.prompts import PromptTemplates
from src.ai.llm_provider import LLMManager
from src.utils.config import Config
from src.utils.logger import LoggerMixin

class DiagramAgent(BaseReviewAgent, LoggerMixin):
    """
    Diagram review agent that analyzes wiring diagrams and visual elements.
    
    Focuses on:
    - Wiring accuracy and connection validation
    - Component identification and labeling
    - Visual clarity and readability
    - Consistency with text instructions
    - Safety-critical connections
    """

    def __init__(self):
        super().__init__(
            role="Diagram and Visual Reviewer",
            goal="Identify wiring errors, unclear visuals, and safety issues in diagrams",
            backstory="You are an experienced electrical engineer who has reviewed thousands of access control wiring diagrams. You understand SECURITRON's, ALARM CONTROLS', HES's, and ADAMS RITE's specific diagramming style and can spot connection errors, missing components, and clarity issues that could confuse field technicians.",
            confidence_threshold=0.7
        )

        # Initialize Mistral client for vision analysis
        self.vision_client = None
        if Config.MISTRAL_API_KEY:
            try:
                import httpx
                self.vision_client = httpx.Client(
                    base_url=Config.MISTRAL_BASE_URL,
                    headers={
                        "Authorization": f"Bearer {Config.MISTRAL_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    timeout=Config.OCR_TIMEOUT
                )
                self.logger.info("Mistral vision client initialized for diagram analysis")
            except Exception as e:
                self.logger.warning("Failed to initialize Mistral vision client", error=str(e))

        # Define critical wiring patterns to check
        self.critical_patterns = {
            "power_polarity": {
                "description": "Power supply polarity connections",
                "severity": "error"
            },
            "fire_alarm": {
                "description": "Fire alarm integration",
                "severity": "error"
            },
            "door_control": {
                "description": "Lock control relay connections",
                "severity": "error"
            },
            "grounding": {
                "description": "Proper grounding connections",
                "severity": "warning"
            },
            "wire_colors": {
                "description": "Wire color consistency",
                "severity": "warning"
            }
        }
    
    def review(self, context: ReviewContext) -> List[AgentFinding]:
        """
        Perform diagram review of the document.
        
        Args:
            context: Review context with document and session info
            
        Returns:
            List of findings with issues identified in the diagram
        """
        findings = []

        # Extract diagram references from context
        diagram_refs = self._extract_diagram_references(context.document_text)

        # if diagrams found, analyze them
        images = getattr(context, 'images', None)
        if images:
            vision_findings = self._analyze_diagrams_with_vision(
                images,
                context.session_id,
                diagram_refs
            )
            findings.extend(vision_findings)

        # perform text-based diagram analysis
        text_findings = self._analyze_diagram_text_references(
            context.document_text,
            context.session_id
        )
        findings.extend(text_findings)

        self.logger.info(
            "Diagram review completed",
            session_id=context.session_id,
            total_findings=len(findings)
        )
        return findings
    
    def _analyze_diagrams_with_vision(
            self,
            images: List[bytes],
            session_id: int,
            diagram_refs: List[str]
    ) -> List[AgentFinding]:
        """Analyze actual diagram images using Mistral vision API."""
        findings = []
        if not self.vision_client:
            self.logger.warning("Vision client not available, skipping images analysis")
            return findings
        
        for idx, image_data in enumerate(images):
            try:
                # Convert image bytes to base64
                img = Image.open(io.BytesIO(image_data))
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode()

                # Analyze diagram with structured prompt
                diagram_findings = self._analyze_single_diagram(
                    img_base64,
                    session_id,
                    f"Diagram {idx + 1}"
                )
                findings.extend(diagram_findings)

            except Exception as e:
                self.logger.error(
                    "Failed to analyze diagram image",
                    diagram_number = idx + 1,
                    error=str(e)
                )
        return findings
    
    def _analyze_single_diagram(
            self,
            img_base64: str,
            session_id: int,
            diagram_ref: str
    ) -> List[AgentFinding]:
        """Analyze a single diagram image"""
        findings = []

        # Structured prompt for diagram analysis
        prompt = """You are reviewing a SECURITRON, ALARM CONTROLS, HES, or ADAMS RITE access control wiring diagram. These diagrams use a specific style optimized for field technicians, not standard electrical schematics.

Diagram Conventions:
- Components shown as labeled boxes (e.g., "BPS-12/24-1" for power supply)
- Connections shown with lines and junction dots
- Terminal labels: C (Common), NO (Normally Open), NC (Normally Closed)
- Products that have wires will have wire colors indicated (e.g., RED for positive, BLK for negative)
- Products that do not have wires will have a terminal label only (e.g., "C", "NO", "NC")
- (+) and (-) symbols for DC polarity
- Ground symbols shown as standard electrical ground

CRITICAL CHECKS (Report ALL issues found):

1. POWER CONNECTIONS (Error if wrong):
   - Verify (+) positive starts at the power supply
   - The (+) of the locking device may be shown as "RED", (+), or INPUT, depending on the product.
   - Verify (-) negative/ground of every device is shown with a grounding symbol
   - The (-) of the locking device may be shown as "BLK", (-), or GND, depending on the product.
   - Check proper polarity on all DC devices
   - Ensure that the C, COM, or COMMON terminals are ONLY connected to the (+) positive - our products are never controlled by breaking the negative in order to ensure safety in case there is a short to ground.

2. FIRE ALARM INTEGRATION (Error if missing/wrong):
   - Must show connection to fire alarm system
   - This may be shown as a direct connection, or through a note that indicates fire alarm integration
   - Should release locks on alarm activation
   - All fail-safe devices must include a fire alarm integration - this may be shown as a direct connection, or through a note that indicates fire alarm integration.
   - All magnetic locks are fail-safe. Other devices may be fail-safe or fail-secure so check that the product is properly identified.

3. LOCK CONTROL RELAY (Error if wrong):
   - C (Common) connections correct and connected to (+) positive
   - NO/NC terminals properly utilized
   - Fail secure devices should be wired in parallel using the NO terminal
   - Fail safe devices should be wired in series using the NC terminal
   - Lock control logic matches intended operation
   - All magnetic locks are fail-safe. Other devices may be fail-safe or fail-secure so check that the product is properly identified.

4. COMPONENT CONNECTIONS (Warning if unclear):
   - All terminals clearly labeled
   - Wire routing traceable from the (+) positive terminal of the power supply to the (+) positive terminal of the locking device.
   - No ambiguous connections
   - All products with a (-) negative terminal should be connected to the (-) negative of the power supply, or to a ground symbol.

5. VISUAL CLARITY (Info if poor):
   - Text legibility
   - Line clarity
   - Component identification

For EACH issue found, respond in this format:
[SEVERITY] - [LOCATION]: [SPECIFIC ISSUE]
Suggestion: [HOW TO FIX]

Example:
[ERROR] - Power Supply Connection: Positive terminal connected to BLACK wire instead of RED
Suggestion: Connect positive (+) terminal to RED wire per color convention

Never say "diagram appears correct" - always list specific issues found. If truly no issues, state "All diagrams appear correct - human review is recommended for validation"."""

        try:
            payload = {
                "model": Config.MISTRAL_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{img_base64}"}
                            }
                        ]
                    }
                ],
                "max_tokens": 1500,
                "temperature": 0.2  # Low temperature for consistent analysis
            }

            if self.vision_client is not None:
                response = self.vision_client.post("/chat/completions", json=payload)
                response.raise_for_status()
                
                result = response.json()
                if "choices" in result and result["choices"]:
                    analysis = result["choices"][0]["message"]["content"]
                    
                    # Parse findings from response
                    parsed_findings = self._parse_vision_findings(
                        analysis, 
                        session_id, 
                        diagram_ref
                    )
                    findings.extend(parsed_findings)
            else:
                self.logger.warning("Vision client is not initialized, skipping vision analysis for this diagram.")
            
        except Exception as e:
            self.logger.error(
                "Vision analysis failed",
                diagram=diagram_ref,
                error=str(e)
            )
            
            # Add a finding about the failure
            findings.append(self.create_finding(
                session_id=session_id,
                severity="warning",
                category="diagram",
                description="Unable to analyze diagram image - manual review required",
                location=diagram_ref,
                suggestion="Ensure diagram is clear and properly scanned",
                confidence=0.9
            ))
        
        return findings
    
    def _parse_vision_findings(
            self,
            analysis: str,
            session_id: int,
            diagram_ref: str) -> List[AgentFinding]:
        """Parse structured findings from vision analysis response."""
        findings = []

        # Split by lines and look for [SEVERITY] tags
        lines = analysis.split('\n')
        current_finding = None

        for line in lines:
            line = line.strip()

            # Check for severity pattern
            severity_match = re.match(r'\[(\w+)\]\s*-\s*([^:]+):\s*(.+)', line)
            if severity_match:
                # Save previous finding if exists
                if current_finding:
                    findings.append(current_finding)

                severity = severity_match.group(1).lower()
                location = f"{diagram_ref} - {severity_match.group(2)}"
                description = severity_match.group(3)

                # validate severity
                if severity not in ['error', 'warning', 'info']:
                    severity = 'warning'

                current_finding = {
                    'severity': severity,
                    'location': location,
                    'description': description,
                    'suggestion': None
                }

            # Check for suggestion
            elif line.lower().startswith("suggestion:") and current_finding:
                current_finding['suggestion'] = line.split(':', 1)[1].strip()

        # Add last finding if exists
        if current_finding:
            findings.append(current_finding)

        # Convert to AgentFinding objects
        agent_findings = []
        for f in findings:
            agent_findings.append(self.create_finding(
                session_id=session_id,
                severity=f['severity'],
                category="diagram",
                description=f['description'],
                location=f['location'],
                suggestion=f.get('suggestion', "No suggestion provided"),
                confidence=0.85  # Default confidence, can be adjusted
            ))

        return agent_findings
    
    def _analyze_diagram_text_references(
            self,
            text: str,
            session_id: int
    ) -> List[AgentFinding]:
        findings = []
        # Check for missing diagram references
        if "wire" in text.lower() or "connect" in text.lower():
            if "diagram" not in text.lower() and "figure" not in text.lower():
                findings.append(self.create_finding(
                    session_id=session_id,
                    severity="warning",
                    category="diagram",
                    description="Wiring instructions provided without diagram reference",
                    location="Document text",
                    suggestion="Add reference to wiring diagram for visual guidance",
                    confidence=0.7
                ))

        # Check for diagram-text consistency markers
        diagram_refs = self._extract_diagram_references(text)
        for ref in diagram_refs:
            # Look for corresponding instructions
            if ref not in text:
                findings.append(self.create_finding(
                    session_id=session_id,
                    severity="info",
                    category="diagram",
                    description=f"Diagram reference '{ref}' found but no corresponding instructions",
                    location=ref,
                    suggestion="Add text instructions that correspond to the diagram",
                    confidence=0.6
                ))

        return findings
    
    def _extract_diagram_references(self, text: str) -> List[str]:
        """Extract diagram references from text"""
        refs = []

        # Common patterns for diagram references
        patterns = [
            r'[Ff]igure\s+\d+',
            r'[Dd]iagram\s+\d+',
            r'[Dd]rawing\s+#?\s*\w+',
            r'[Ww]iring\s+[Dd]iagram',
            r'[Ss]ee\s+[Dd]iagram'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            refs.extend(matches)

        return list(set(refs)) # Remove duplicates
    
    def _check_specific_wiring_patterns(
            self,
            text: str,
            session_id: int
    ) -> list[AgentFinding]:
        """Check for specific wiring patterns that are commonly problematic."""
        findings = []

        # Pattern 1: Fire alarm connections
        if "fire alarm" in text.lower():
            if "fail safe" not in text.lower() and "normally closed" not in text.lower():
                findings.append(self.create_finding(
                    session_id=session_id,
                    severity="error",
                    category="safety",
                    description="Fire alarm integration mentioned without fail-safe configuration details",
                    location="Fire alarm section",
                    suggestion="Specify fail-safe wiring configuration for fire alarm integration",
                    confidence=0.8
                ))
        
        # Pattern 2: Power polarity
        if "12vdc" in text.lower() or "24vdc" in text.lower():
            if "polarity" not in text.lower() and "positive" not in text.lower():
                findings.append(self.create_finding(
                    session_id=session_id,
                    severity="warning",
                    category="wiring",
                    description="DC voltage specified without polarity warnings",
                    location="Power specifications",
                    suggestion="Add warning about correct polarity connection",
                    confidence=0.7
                ))
        
        # Pattern 3: Lock type specificity
        if "maglock" in text.lower() or "magnetic lock" in text.lower():
            if "fire alarm" not in text.lower() and "fail safe" not in text.lower():
                findings.append(self.create_finding(
                    session_id=session_id,
                    severity="info",
                    category="specification",
                    description="Magnetic lock mentioned without fail-safe or fire alarm integration details",
                    location="Lock specifications",
                    suggestion="Clarify that magnetic locks are fail-safe and should integrate with fire alarm systems",
                    confidence=0.6
                ))
        
        return findings