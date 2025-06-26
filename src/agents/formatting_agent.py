# src/agents/formatting_agent.py
"""Comprehensive formatting and standards compliance agent"""

import re
import math
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass

from src.agents.base_agent import BaseReviewAgent, ReviewContext
from src.storage.models import AgentFinding
from src.ai.prompts import PromptTemplates
from src.ai.llm_provider import LLMManager
from src.utils.config import Config


@dataclass
class ConversionRule:
    """Rule for unit conversion validation"""
    pattern: str
    from_unit: str
    to_unit: str
    conversion_factor: Optional[float]
    tolerance: float = 0.1  # Acceptable rounding tolerance


class FormattingAgent(BaseReviewAgent):
    """
    Comprehensive formatting agent that specializes in:
    - Imperial/Metric conversion accuracy
    - Temperature conversion validation  
    - Fraction notation error detection
    - Format standardization enforcement
    - Unit consistency checking
    """
    
    def __init__(self):
        super().__init__(
            role="Formatting and Standards Reviewer",
            goal="Ensure mathematical accuracy, format consistency, and compliance with company formatting standards",
            backstory="You are a meticulous technical editor with expertise in measurement systems, mathematical conversions, and SECURITRON/ASSA ABLOY documentation standards. You catch the subtle formatting errors that automated systems miss and ensure professional presentation quality.",
            confidence_threshold=0.8
        )
        
        # Initialize LLM manager if available
        self.llm_manager = None
        if Config.GROQ_API_KEY or Config.GEMINI_API_KEY:
            try:
                self.llm_manager = LLMManager()
            except Exception as e:
                self.logger.warning("Failed to initialize LLM Manager", error=str(e))
        
        # Define conversion rules and validation patterns
        self._setup_conversion_rules()
        self._setup_format_patterns()
        self._setup_company_standards()

    def _setup_conversion_rules(self):
        """Setup mathematical conversion validation rules"""
        self.conversion_rules = [
            # Temperature conversions (F to C: (F-32) * 5/9)
            ConversionRule(
                pattern=r'(-?\d+(?:\.\d+)?)\s*°?F.*?(-?\d+(?:\.\d+)?)\s*°?C',
                from_unit="F",
                to_unit="C", 
                conversion_factor=None,  # Custom validation
                tolerance=0.5
            ),
            # Length conversions
            ConversionRule(
                pattern=r'(\d+(?:\.\d+)?)\s*(?:inch|in|").*?(\d+(?:\.\d+)?)\s*(?:mm|millimeter)',
                from_unit="inch",
                to_unit="mm",
                conversion_factor=25.4,
                tolerance=0.5
            ),
            ConversionRule(
                pattern=r'(\d+(?:\.\d+)?)\s*(?:ft|foot|feet).*?(\d+(?:\.\d+)?)\s*(?:m|meter)',
                from_unit="ft",
                to_unit="m",
                conversion_factor=0.3048,
                tolerance=0.01
            ),
        ]
    
    def _setup_format_patterns(self):
        """setup format validation patterns."""
        # Fraction patterns that should be caught
        self.problematic_patterns = {
            # Common fraction notation errors
            # Imperial measurements using decimals (should use fractions)
            'imperial_decimal_instead_of_fraction': {
                'pattern': r'\b\d+\.\d+\s*(?:inch|in|"|\s*\[)',
                'description': 'Imperial measurement using decimal instead of fraction notation',
                'examples': ['1.5 inch', '2.25"', '3.75 inches'],
                'correct_format': 'Use fractional notation for imperial: 1-1/2", 2-1/4", 3-3/4"'
            },
            # Metric measurements using fractions (should use decimals)
            'metric_fraction_instead_of_decimal': {
                'pattern': r'\b\d+(?:\s*-\s*)?\d*/\d+\s*(?:mm|cm|millimeter|centimeter)',
                'description': 'Metric measurement using fraction instead of decimal notation',
                'examples': ['25-1/2 mm', '3/4 cm', '1-1/8 millimeters'],
                'correct_format': 'Use decimal notation for metric: 25.5mm, 0.8cm, 28.6mm'
            },
            # Excessive decimal precision in metric (should be 1 decimal place max)
            'metric_excessive_precision': {
                'pattern': r'\b\d+\.\d{2,}\s*(?:mm|cm|millimeter|centimeter)',
                'description': 'Metric measurement with excessive decimal precision',
                'examples': ['25.40mm', '38.100mm', '12.345mm'],
                'correct_format': 'Use 1 decimal place maximum for metric: 25.4mm, 38.1mm, 12.3mm'
            },
            
            # Missing units on measurements
            'measurements_without_units': {
                'pattern': r'\b(?:diameter|length|width|height|distance|gap|clearance|spacing)\s+(?:of\s+)?(\d+(?:\.\d+)?(?:\s*[-]\s*\d+(?:\.\d+)?)?)\s*(?!["\w]|mm|cm|in|inch|ft|foot|meter|m\b)',
                'description': 'Measurement values without units specified',
                'examples': ['diameter of 2', 'length 15', 'spacing 1-1/2'],
                'correct_format': 'Always specify units: 2", 15mm, 1-1/2"'
            }
        }
        # Unit consistency patterns
        self.unit_patterns = {
            'imperial_inch': r'\d+(?:\.\d+|\s*-\s*\d+(?:/\d+)?)\s*(?:inch|in|")',
            'metric_mm': r'\d+(?:\.\d+)?\s*(?:mm|millimeter)',
            'metric_cm': r'\d+(?:\.\d+)?\s*(?:cm|centimeter)', 
            'imperial_ft': r'\d+(?:\.\d+|\s*-\s*\d+(?:/\d+)?)\s*(?:ft|foot|feet)',
            'metric_m': r'\d+(?:\.\d+)?\s*(?:m|meter)(?!m)',  # Not mm
            'temperature_f': r'-?\d+(?:\.\d+)?\s*°?F',
            'temperature_c': r'-?\d+(?:\.\d+)?\s*°?C'
        }
    
    def _setup_company_standards(self):
        """Setup Securitron/HES/Adams Rite/Alarm Controls specific formatting standards."""
        self.company_standards = {
            # Imperial measurements should use fractions, not decimals
            'imperial_fraction_format': {
                'pattern': r'\d+(?:\s*-\s*\d+/\d+)?\s*(?:inch|in|")',  # e.g., "1-1/2"" or "3/4""
                'description': 'Imperial measurements must use fractional notation',
                'examples': ['1"', '1-1/2"', '3/4"', '2-1/4"'],
                'avoid': ['1.0"', '1.5"', '0.75"', '2.25"']
            },
            # Metric measurement standards (always decimal, 1 decimal place max)
            'metric_decimal_format': {
                'pattern': r'\d+(?:\.\d)?\s*(?:mm|cm|m)(?!m)',  # e.g., "25.4mm"
                'description': 'Metric measurements must use decimal notation (1 decimal place max)',
                'examples': ['25.4mm', '38.1mm', '12.7mm', '50mm'],
                'avoid': ['25-1/2mm', '38-1/8mm', '25.40mm', '38.100mm']
            },
            
            # Standard format: Imperial primary with metric in brackets
            'primary_secondary_format': {
                'pattern': r'\d+(?:\s*-\s*\d+/\d+)?\s*(?:inch|in|")\s*\[\d+(?:\.\d)?\s*mm\]',
                'description': 'Standard format: Imperial primary with metric in brackets',
                'examples': ['1" [25.4mm]', '1-1/2" [38.1mm]', '3/4" [19.1mm]'],
                'correct_format': 'Always use: Imperial [metric] format'
            },
            
            # Standard measurement formats
            'fraction_format': {
                'pattern': r'\d+\s*-\s*\d+/\d+',  # e.g., "1-1/2"
                'description': 'Standard mixed fraction format with dash separator'
            },
            'imperial_units': {
                'primary': '"',  # Preferred inch symbol
                'acceptable': ['inch', 'in'],
                'avoid': ['"', '″']  # Curly quotes, double prime
            },
            'metric_brackets': {
                'pattern': r'\[(\d+(?:\.\d)?)\s*(mm|cm|m)\]',
                'description': 'Metric measurements in brackets as secondary units'
            },
            'temperature_format': {
                'imperial': '°F',
                'metric': '°C',
                'avoid_symbols': ['F', 'C', 'deg F', 'deg C']
            }
        }
    
    def review(self, context: ReviewContext) -> List[AgentFinding]:
        """
        Perform comprehensive formatting and standards compliance review.
        
        Args:
            context: Review context with document and session info
        
        Returns:
            List of formatting findings
        """
        findings = []

        # AI-powered review if available
        if self.llm_manager:
            ai_findings = self._perform_ai_formatting_review(context)
            findings.extend(ai_findings)

        # Rule-based formatting checks (always performed)
        rule_findings = self._perform_rule_based_review(context)
        findings.extend(rule_findings)

        self.logger.info(
            "Formatting review completed",
            session_id=context.session_id,
            ai_findings=len(ai_findings) if self.llm_manager else 0,
            rule_findings=len(rule_findings),
            total_findings=len(findings)
        )

        return findings

    def _validate_imperial_metric_standards(self, text: str, session_id: int) -> List[AgentFinding]:
        """
        Validate company-sepcific imperial/metric standards compliance.
        """
        findings = []

        # Check for imperial measurements using decimals instead of fractions
        imperial_decimal_pattern = r'\b(\d+\.\d+)\s*(?:inch|in|")'
        imperial_decimal_matches = re.finditer(imperial_decimal_pattern, text, re.IGNORECASE)

        for match in imperial_decimal_matches:
            decimal_value = float(match.group(1))
            # convert to nearest fraction
            suggested_fraction = self._decimal_to_fraction(decimal_value)

            findings.append(self.create_finding(
                session_id=session_id,
                severity="warning",
                category="standards",
                description=f"Imperial measurement using decimal notation: '{match.group(0)}'",
                location=f"Measurement: {match.group(0)}",
                suggestion=f"Use fractional notation: {suggested_fraction}",
                confidence=0.9
            ))
        # Check for metric measurements using fractions instead of decimals
        metric_fraction_pattern = r'\b(\d+(?:\s*-\s*)?\d*/\d+)\s*(mm|cm|millimeter|centimeter)'
        metric_fraction_matches = re.finditer(metric_fraction_pattern, text, re.IGNORECASE)
        
        for match in metric_fraction_matches:
            fraction_text = match.group(1)
            unit = match.group(2)
            # Convert fraction to decimal
            try:
                decimal_value = self._fraction_to_decimal(fraction_text)
                # Round to 1 decimal place per company standard
                rounded_decimal = round(decimal_value, 1)
                
                findings.append(self.create_finding(
                    session_id=session_id,
                    severity="warning",
                    category="standards",
                    description=f"Metric measurement using fraction notation: '{match.group(0)}'",
                    location=f"Measurement: {match.group(0)}",
                    suggestion=f"Use decimal notation: {rounded_decimal}{unit}",
                    confidence=0.9
                ))
            except:
                # If fraction parsing fails, still flag as non-standard
                findings.append(self.create_finding(
                    session_id=session_id,
                    severity="warning",
                    category="standards",
                    description=f"Metric measurement using non-standard notation: '{match.group(0)}'",
                    location=f"Measurement: {match.group(0)}",
                    suggestion=f"Use decimal notation for metric measurements",
                    confidence=0.8
                ))
            # Check for metric measurements with excessive precision (>1 decimal place)
        excessive_precision_pattern = r'\b(\d+\.\d{2,})\s*(mm|cm|millimeter|centimeter)'
        precision_matches = re.finditer(excessive_precision_pattern, text, re.IGNORECASE)
        
        for match in precision_matches:
            value = float(match.group(1))
            unit = match.group(2)
            rounded_value = round(value, 1)
            
            findings.append(self.create_finding(
                session_id=session_id,
                severity="info",
                category="precision",
                description=f"Metric measurement with excessive precision: '{match.group(0)}'",
                location=f"Measurement: {match.group(0)}",
                suggestion=f"Round to 1 decimal place: {rounded_value}{unit}",
                confidence=0.8
            ))
        
        # Validate imperial/metric pairing format
        pairing_pattern = r'(\d+(?:\s*-\s*\d+/\d+)?)\s*(?:inch|in|")\s*\[(\d+(?:\.\d+)?)\s*(mm|cm)\]'
        pairing_matches = re.finditer(pairing_pattern, text, re.IGNORECASE)
        
        for match in pairing_matches:
            imperial_text = match.group(1)
            metric_value = float(match.group(2))
            metric_unit = match.group(3).lower()
            
            # Check if metric has proper precision (1 decimal place max)
            if '.' in match.group(2) and len(match.group(2).split('.')[1]) > 1:
                rounded_metric = round(metric_value, 1)
                findings.append(self.create_finding(
                    session_id=session_id,
                    severity="info",
                    category="precision",
                    description=f"Metric conversion has excessive precision: '[{match.group(2)}{metric_unit}]'",
                    location=f"Conversion: {match.group(0)}",
                    suggestion=f"Round to 1 decimal place: [{rounded_metric}{metric_unit}]",
                    confidence=0.8
                ))
        
        return findings
    
    def _decimal_to_fraction(self, decimal_value: float) -> str:
        """Convert decimal to nearest standard fraction"""
        # Common fractions used in technical documentation
        fractions = {
            0.0625: "1/16",    0.125: "1/8",     0.1875: "3/16",   0.25: "1/4",
            0.3125: "5/16",    0.375: "3/8",     0.4375: "7/16",   0.5: "1/2",
            0.5625: "9/16",    0.625: "5/8",     0.6875: "11/16",  0.75: "3/4",
            0.8125: "13/16",   0.875: "7/8",     0.9375: "15/16"
        }

        whole_part = int(decimal_value)
        fractional_part = decimal_value - whole_part

        # find closest fraction
        closest_fraction = None
        min_diff = float('inf')

        for frac_decimal, frac_text in fractions.items():
            diff = abs(fractional_part - frac_decimal)
            if diff < min_diff:
                min_diff = diff
                closest_fraction = frac_text

        if whole_part > 0 and closest_fraction and fractional_part > 0.03: # threshold for rounding
            return f"{whole_part}-{closest_fraction}"
        elif closest_fraction and fractional_part > 0.03:  # threshold for rounding
            return closest_fraction
        else:
            return str(whole_part)
        
    def _fraction_to_decimal(self, fraction_text: str) -> float:
        """Convert fraction text to decimal value"""
        if '-' in fraction_text:
            # mixed fraction
            parts = fraction_text.split('-')
            whole = int(parts[0].strip())
            frac_part = parts[1].strip()
        else:
            # simple fraction
            whole = 0
            frac_part = fraction_text.strip()

        # parse the fraction part
        if '/' in frac_part:
            numerator, denominator = frac_part.split('/')
            fraction_value = int(numerator) / int(denominator)
        else:
            fraction_value = 0

        return whole + fraction_value
    
    def _perform_ai_formatting_review(self, context: ReviewContext) -> List[AgentFinding]:
        """Perform AI-based formatting review on the given context with specialized prompts."""
        findings = []

        if not self.llm_manager:
            return findings
        
        try:
            # Use specialized formatting prompt
            prompt = PromptTemplates.get_agent_prompt("formatting", context.document_text)

            response = self.llm_manager.generate_response(
                prompt,
                max_tokens=Config.MAX_TOKENS_PER_REQUEST,
                temperature=0.1 # very low temperature for deterministic output
            )

            ai_findings = self._parse_ai_response(response, context.session_id)
            findings.extend(ai_findings)

        except Exception as e:
            self.logger.error("Ai formatting review failed", error=str(e))

        return findings
    
    def _parse_ai_response(self, response: str, session_id: int) -> List[AgentFinding]:
        """Parse AI response into structured findings."""
        findings = []

        try:
            # Look for findings section
            if "FINDINGS:" in response:
                findings_section = response.split("FINDINGS:")[1].strip()
            else:
                findings_section = response

            # Split by separator patterns
            raw_findings = re.split(r'---+|\n\n\n+', findings_section)

            for raw_finding in raw_findings:
                finding = self._parse_single_ai_finding(raw_finding.strip(), session_id)
                if finding:
                    findings.append(finding)

        except Exception as e:
            self.logger.error("Failed to parse AI response", error=str(e))

        return findings
    
    def _parse_single_ai_finding(self, raw_finding: str, session_id: int) -> Optional[AgentFinding]:
        """Parse a single AI finding from the raw text."""
        if not raw_finding or len(raw_finding) < 10:
            return None
        
        try:
            lines = raw_finding.split('\n')
            main_line = lines[0] if lines else ""

            # Extract severity and content
            severity_match = re.match(r'\[?(\w+)\]?\s*-\s*(.+)', main_line)
            if not severity_match:
                return None
            
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

            # Look for suggestion
            suggestion = None
            for line in lines[1:]:
                if line.strip().lower().startswith('suggestion:'):
                    suggestion = line.split(':', 1)[1].strip()
                    break
            
            # Validate severity
            if severity not in ['error', 'warning', 'info']:
                severity = 'warning'

            return self.create_finding(
                session_id=session_id,
                severity=severity,
                category="formatting",
                description=description,
                location=location,
                suggestion=suggestion,
                confidence=0.8  # Default confidence, can be adjusted based on context
            )

        except Exception as e:
            self.logger.error("Failed to parse single AI finding", error=str(e))
            return None
    
    def _perform_rule_based_review(self, context: ReviewContext) -> List[AgentFinding]:
        """Perform comprehensive rule-based formatting review"""
        findings = []
        text = context.document_text
        
        # Mathematical conversion validation
        findings.extend(self._validate_conversions(text, context.session_id))
        
        # Format pattern validation
        findings.extend(self._check_format_patterns(text, context.session_id))
        
        # Unit consistency validation
        findings.extend(self._check_unit_consistency(text, context.session_id))
        
        # Company standards compliance
        findings.extend(self._check_company_standards(text, context.session_id))
        
        # Imperial/metric format compliance (company-specific)
        findings.extend(self._validate_imperial_metric_standards(text, context.session_id))
        
        # Advanced fraction analysis
        findings.extend(self._analyze_fraction_usage(text, context.session_id))
        
        return findings
    
    def _validate_conversions(self, text: str, session_id: int) -> List[AgentFinding]:
        """Validate mathematical accuracy of conversions"""
        findings = []

        for rule in self.conversion_rules:
            matches = re.finditer(rule.pattern, text, re.IGNORECASE)
            
            for match in matches:
                try:
                    value1 = float(match.group(1))
                    value2 = float(match.group(2))

                    if rule.from_unit == "F" and rule.to_unit == "C":
                        # Temperature conversion validation
                        expected_c = (value1 - 32) * 5 / 9
                        if abs(value2 - expected_c) > rule.tolerance:
                            findings.append(self.create_finding(
                                session_id=session_id,
                                severity="error",
                                category="conversion",
                                description=f"Incorrect temperature conversion: {value1}°F should be {expected_c:.1f}°C, not {value2}°C",
                                location=f"Conversion: {match.group(0)}",
                                suggestion=f"Correct conversion: {value1}°F = {expected_c:.1f}°C",
                                confidence=0.95
                            ))
                    
                    elif rule.conversion_factor:
                        # Linear conversion validation
                        expected_value = value1 * rule.conversion_factor
                        if abs(value2 - expected_value) > rule.tolerance:
                            findings.append(self.create_finding(
                                session_id=session_id,
                                severity="error",
                                category="conversion",
                                description=f"Incorrect conversion: {value1} {rule.from_unit} should be {expected_value:.1f} {rule.to_unit}, not {value2} {rule.to_unit}",
                                location=f"Conversion: {match.group(0)}",
                                suggestion=f"Correct conversion: {value1} {rule.from_unit} = {expected_value:.1f} {rule.to_unit}",
                                confidence=0.95
                            ))
                    
                except (ValueError, IndexError) as e:
                    self.logger.warning("Could not validate conversion", error=str(e))
        
        return findings
    
    def _check_format_patterns(self, text: str, session_id: int) -> List[AgentFinding]:
        """Check for problematic formatting patterns"""
        findings = []

        for pattern_name, pattern_info in self.problematic_patterns.items():
            matches = re.finditer(pattern_info['pattern'], text, re.IGNORECASE)

            for match in matches:
                # Skip if it's actually a valid usage (e.g., voltage ratiings like 12-24V)
                if self._is_valid_exception(match.group(0)):
                    continue

                severity = "warning" if pattern_name == "mixed_decimal_fraction" else "error"

                findings.append(self.create_finding(
                    session_id=session_id,
                    severity=severity,
                    category="formatting",
                    description=f"{pattern_info['description']}: '{match.group(0)}'",
                    location=f"Text: {self._get_context_around_match(text, match)}",
                    suggestion=pattern_info['correct_format'],
                    confidence=0.9
                ))
        
        return findings
    
    def _check_unit_consistency(self, text: str, session_id: int) -> List[AgentFinding]:
        """Check for unit consistency acrouss the document"""
        findings = []

        # Count usage of different unit systems
        unit_counts = {}
        for unit_type, pattern in self.unit_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            unit_counts[unit_type] = len(matches)

        # Check for mixed systems
        imperial_count = unit_counts.get('imperial_inch', 0) + unit_counts.get('imperial_ft', 0)
        metric_count = unit_counts.get('metric_mm', 0) + unit_counts.get('metric_cm', 0) + unit_counts.get('metric_m', 0)

        if imperial_count > 0 and metric_count > 0:
            # Mixed systems - check if metric is properly bracketed
            metric_in_brackets = len(re.findall(r'\[\d+(?:\.\d+)?\s*(?:mm|cm|m)\]', text))
            standalone_metric = metric_count - metric_in_brackets

            if standalone_metric > 0:
                findings.append(self.create_finding(
                    session_id=session_id,
                    severity="warning",
                    category="consistency",
                    description=f"Mixed unit systems detected: {imperial_count} imperial units and {metric_count} metric units",
                    location="Document",
                    suggestion="use imperial as primary with metric in brackets [25.4mm] or standardize on one system.",
                    confidence=0.8
                ))
        
        # Check temperature unit consistency
        temp_f_count = unit_counts.get('temperature_f', 0)
        temp_c_count = unit_counts.get('temperature_c', 0)
        
        if temp_f_count > 0 and temp_c_count > 0:
            findings.append(self.create_finding(
                session_id=session_id,
                severity="info",
                category="consistency",
                description=f"Mixed temperature units: {temp_f_count} Fahrenheit, {temp_c_count} Celsius",
                location="Temperature references",
                suggestion="Consider standardizing on one temperature scale or clearly indicate conversions",
                confidence=0.7
            ))
        
        return findings

    def _check_company_standards(self, text: str, session_id: int) -> List[AgentFinding]:
        """Check compliance iwth company-specific formatting standards"""
        findings = []

        # Check for non-standard inch symbols
        wrong_inch_symbols = re.finditer(r'\d+(?:\.\d+)?\s*[″"'']', text)
        for match in wrong_inch_symbols:
            findings.append(self.create_finding(
                session_id=session_id,
                severity="warning",
                category="standards",
                description=f"Non-standard inch symbol used: '{match.group(0)}'",
                location=f"Measurement: {match.group(0)}",
                suggestion='Use standard " symbol for inches',
                confidence=0.9
            ))
        
        # Check for improper temperature symbols
        wrong_temp_symbols = re.finditer(r'\d+\s*(?:deg\s*[FC]|[FC](?!\s*[a-z]))', text)
        for match in wrong_temp_symbols:
            findings.append(self.create_finding(
                session_id=session_id,
                severity="warning", 
                category="standards",
                description=f"Non-standard temperature format: '{match.group(0)}'",
                location=f"Temperature: {match.group(0)}",
                suggestion="Use standard °F or °C symbols for temperature",
                confidence=0.9
            ))
        
        return findings
    
    def _analyze_fraction_usage(self, text: str, session_id: int) -> List[AgentFinding]:
        """Advanced analysis of fraction notation usage"""
        findings = []
        
        # Find all potential fraction-like patterns
        fraction_patterns = [
            r'\b\d+\s*-\s*\d+/\d+\b',  # Standard: 1-1/2
            r'\b\d+/\d+\b',            # Simple: 3/4
            r'\b\d+\s*-\s*\d+\b',      # Problem: 1-2 (should be 1-1/2?)
            r'\b\d+\.\d+\b'            # Decimal: 1.5
        ]
        
        all_fractions = []
        for pattern in fraction_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                # Skip if it's clearly not a measurement (voltage, model numbers, etc.)
                if not self._looks_like_measurement(text, match):
                    continue
                all_fractions.append({
                    'text': match.group(0),
                    'start': match.start(),
                    'end': match.end(),
                    'type': self._classify_fraction_type(match.group(0))
                })
        
        # Analyze consistency
        if len(all_fractions) > 1:
            types_used = set(f['type'] for f in all_fractions)
            if len(types_used) > 1:
                findings.append(self.create_finding(
                    session_id=session_id,
                    severity="info",
                    category="consistency",
                    description=f"Mixed fraction notation styles used: {', '.join(types_used)}",
                    location="Throughout document",
                    suggestion="Standardize on one fraction notation style (preferably 1-1/2 format)",
                    confidence=0.7
                ))
        
        return findings
    
    def _is_valid_exception(self, text: str) -> bool:
        """Check if a pattern match is actually a valid exception"""
        # Common exceptions that look like dash-fractions but aren't
        exceptions = [
            r'\d+-\d+\s*(?:V|VDC|VAC|volt)',  # Voltage ranges
            r'\d+-\d+\s*(?:Hz|kHz|MHz)',      # Frequency ranges  
            r'\d+-\d+\s*(?:amp|mA|A)',        # Current ranges
            r'\d+-\d+\s*(?:ohm|Ω)',           # Resistance ranges
            r'\w+\d+-\d+',                    # Model numbers
        ]
        
        for exception in exceptions:
            if re.match(exception, text, re.IGNORECASE):
                return True
        return False
    
    def _looks_like_measurement(self, full_text: str, match) -> bool:
        """Determine if a match is likely a measurement value"""
        # Get context around the match
        start = max(0, match.start() - 20)
        end = min(len(full_text), match.end() + 20)
        context = full_text[start:end].lower()
        
        # Measurement indicators
        measurement_words = [
            'inch', 'inches', 'mm', 'millimeter', 'cm', 'centimeter',
            'diameter', 'length', 'width', 'height', 'clearance', 'gap',
            'spacing', 'distance', 'thickness', 'depth', 'size'
        ]
        
        return any(word in context for word in measurement_words)
    
    def _classify_fraction_type(self, fraction_text: str) -> str:
        """Classify the type of fraction notation"""
        if re.match(r'\d+\s*-\s*\d+/\d+', fraction_text):
            return "mixed_fraction"  # 1-1/2
        elif re.match(r'\d+/\d+', fraction_text):
            return "simple_fraction"  # 3/4
        elif re.match(r'\d+\.\d+', fraction_text):
            return "decimal"  # 1.5
        elif re.match(r'\d+\s*-\s*\d+', fraction_text):
            return "dash_notation"  # 1-2 (problematic)
        else:
            return "unknown"
    
    def _get_context_around_match(self, text: str, match, context_length: int = 30) -> str:
        """Get context text around a regex match"""
        start = max(0, match.start() - context_length)
        end = min(len(text), match.end() + context_length)
        context = text[start:end].strip()
        
        # Add ellipsis if truncated
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."
        
        return context