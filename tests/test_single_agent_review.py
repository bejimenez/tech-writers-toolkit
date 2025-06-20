#!/usr/bin/env python3
"""
Test script for Phase 2 Step 2: Simple Single-Agent Review
Use this to test agent functionality without running the full application
"""

import sys
from pathlib import Path
import tempfile

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import Config
from src.utils.logger import setup_logging, get_logger
from src.storage.models import DatabaseManager

def create_test_document() -> Path:
    """Create a test document with known issues"""
    test_content = """
# Installation Instructions for Access Control Panel

## Overview
This document provides installation instructions for the XYZ-200 access control panel.

## Installation Steps

1. Mount the panel to the wall using 4 screws
2. Connect the power cable to the main power source
3. Wire the door contacts to terminals 1 and 2
4. Connect the reader cable to the communication port
5. Test the system by presenting a card to the reader

## Wiring Details
Connect red wire to positive terminal. Connect black wire to negative terminal.
Use 18 gauge wire for all connections. Make sure connections are tight.

## Troubleshooting
If the system doesn't work, check all connections.
"""
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write(test_content)
    temp_file.close()
    
    return Path(temp_file.name)

def test_step2():
    """Test Step 2 implementation"""
    
    # Setup logging
    setup_logging()
    logger = get_logger(__name__)
    
    print("Phase 2 Step 2 Test: Simple Single-Agent Review")
    print("=" * 60)
    
    # Test 1: Configuration
    print("\n1. Testing Configuration...")
    config_errors = Config.validate_config()
    if config_errors:
        print("❌ Configuration errors:")
        for error in config_errors:
            print(f"   - {error}")
        print("\nPlease update your .env file and try again.")
        return False
    print("✅ Configuration validated")
    
    # Test 2: Database Setup
    print("\n2. Testing Database Setup...")
    try:
        db_manager = DatabaseManager()
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False
    
    # Test 3: Technical Agent Initialization
    print("\n3. Testing Technical Agent...")
    try:
        from src.agents.technical_agent import TechnicalAgent
        tech_agent = TechnicalAgent()
        print("✅ Technical Agent initialized")
        print(f"   Role: {tech_agent.role}")
        print(f"   Goal: {tech_agent.goal}")
        print(f"   Has LLM: {tech_agent.llm_manager is not None}")
    except Exception as e:
        print(f"❌ Technical Agent initialization failed: {e}")
        return False
    
    # Test 4: Agent Manager
    print("\n4. Testing Agent Manager...")
    try:
        from src.ai.agent_manager import AgentManager
        agent_manager = AgentManager()
        available_agents = agent_manager.get_available_agents()
        print("✅ Agent Manager initialized")
        print(f"   Available agents: {available_agents}")
    except Exception as e:
        print(f"❌ Agent Manager initialization failed: {e}")
        return False
    
    # Test 5: Document Processing
    print("\n5. Testing Document Processing...")
    try:
        from src.document.processor import DocumentProcessor
        
        # Create test document
        test_file = create_test_document()
        print(f"   Created test document: {test_file.name}")
        
        # Process document
        processor = DocumentProcessor()
        processed_doc = processor.process_document(test_file, user_id="test_user")
        
        print("✅ Document processed successfully")
        print(f"   Session ID: {processed_doc.session_id}")
        print(f"   Text length: {len(processed_doc.text)} characters")
        print(f"   Processing time: {processed_doc.processing_time:.2f}s")
        
        # Clean up
        test_file.unlink()
        
    except Exception as e:
        print(f"❌ Document processing failed: {e}")
        return False
    
    # Test 6: Agent Review Process
    print("\n6. Testing Agent Review Process...")
    try:
        # Start agent review
        print("   Starting agent review...")
        review_result = agent_manager.start_review(processed_doc)
        
        print("✅ Agent review completed")
        print(f"   Status: {review_result.status}")
        print(f"   Total findings: {len(review_result.findings)}")
        print(f"   Processing time: {review_result.total_processing_time:.2f}s")
        
        # Show findings summary
        if review_result.findings:
            print("\n   📋 Findings Summary:")
            severity_counts = {"error": 0, "warning": 0, "info": 0}
            for finding in review_result.findings:
                severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
            
            for severity, count in severity_counts.items():
                if count > 0:
                    print(f"      {severity.title()}s: {count}")
            
            print(f"\n   📝 Summary: {review_result.summary}")
            
            # Show sample findings
            print("\n   🔍 Sample Findings:")
            for i, finding in enumerate(review_result.findings[:3]):  # Show first 3
                print(f"      {i+1}. [{finding.severity.upper()}] {finding.location}")
                print(f"         {finding.description}")
                if finding.suggestion:
                    print(f"         💡 {finding.suggestion}")
                print()
        else:
            print("   No findings detected")
        
    except Exception as e:
        print(f"❌ Agent review failed: {e}")
        logger.exception("Agent review test failed")
        return False
    
    # Test 7: Database Storage Verification
    print("\n7. Testing Database Storage...")
    try:
        # Get findings from database
        stored_findings = db_manager.get_session_findings(processed_doc.session_id)
        print(f"✅ Findings stored and retrieved successfully")
        print(f"   Stored findings: {len(stored_findings)}")
        
        # Verify finding details
        if stored_findings:
            sample_finding = stored_findings[0]
            print(f"   Sample finding ID: {sample_finding.id}")
            print(f"   Agent: {sample_finding.agent_name}")
            print(f"   Category: {sample_finding.category}")
        
    except Exception as e:
        print(f"❌ Database storage verification failed: {e}")
        return False
    
    # Test 8: Agent Testing Function
    print("\n8. Testing Agent Validation...")
    try:
        agent_test_results = agent_manager.test_agents()
        print("✅ Agent testing completed")
        for agent_name, result in agent_test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {agent_name}: {status}")
    except Exception as e:
        print(f"❌ Agent testing failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Step 2 Test PASSED!")
    print("\nWhat you can now do:")
    print("1. Run the main application: python src/main.py")
    print("2. Upload a document in the Review tab")
    print("3. Click 'Start AI Review' to see actual agent findings")
    print("4. View detailed results with severity levels and suggestions")
    print("\nStep 2 Features Implemented:")
    print("✅ Technical Agent with AI and rule-based analysis")
    print("✅ Agent Manager for coordination")
    print("✅ Database storage of findings")
    print("✅ Structured review results with summaries")
    print("✅ Integration with existing UI")
    print("\nNext: Implement Step 3 (Multi-Agent System)")
    
    return True

if __name__ == "__main__":
    success = test_step2()
    sys.exit(0 if success else 1)