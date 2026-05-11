#!/usr/bin/env python3
"""
Demo Script: Multi-Agent Logistics System - Test Scenarios

This script runs the system through several predefined scenarios to demonstrate:
1. Successful route planning
2. Constraint violation detection
3. Alternative suggestions
4. RAG contextual awareness
"""

import os
from dotenv import load_dotenv
from src.orchestrator import build_orchestrator

# Load environment variables
load_dotenv()

def print_header(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"REPORT: {title}")
    print("="*70)

def print_scenario(scenario_num, description):
    """Print scenario information."""
    print(f"\nSCENARIO {scenario_num}: {description}")
    print("-" * 70)

def run_scenario(scenario_num, description, request):
    """Run a single scenario."""
    print_scenario(scenario_num, description)
    print(f"Client Request: {request}\n")
    
    try:
        app = build_orchestrator()
        
        # Initial state
        state = {
            "user_request": request,
            "rag_context": "",
            "analysis_plan": "",
            "validation_report": "",
            "final_response": ""
        }
        
        # Run the orchestrator
        final_state = app.invoke(state)
        
        # Display results
        if final_state and "final_response" in final_state:
            print("\n" + "─" * 70)
            print("SYSTEM RESPONSE:")
            print("-" * 70)
            print(final_state["final_response"])
        else:
            print("System could not generate a response.")
            
    except Exception as e:
        print(f"Error in scenario: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all demo scenarios."""
    
    print_header("LOGISTICS MULTI-AGENT SYSTEM - DEMO SCENARIOS")
    print("\nThis demo runs multiple scenarios to showcase the system's capabilities.")
    print("Each scenario will execute the full agent pipeline.")
    print("\nScenarios to run:")
    print("  1. Simple transport within city limits")
    print("  2. Inter-city transport with highway tolls")
    print("  3. Constraint violation detection")
    print("  4. Truck maintenance issue handling")
    print("  5. Peak time restriction management")
    print("  6. Heavy cargo routing")
    
    # Check API key
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        print("\nERROR: GROQ_API_KEY not configured!")
        print("   Please set up your .env file with a valid Groq API key.")
        return
    
    print("\nAPI key configured. Starting scenarios...\n")
    
    # Scenario 1: Simple transport within city
    run_scenario(
        1,
        "Simple Transport Within City",
        "I need to transport 8 tons of office supplies from Rabat to Casablanca (14:00 departure). Which truck do you recommend?"
    )
    
    # Scenario 2: Inter-city transport with highways
    run_scenario(
        2,
        "Inter-City Highway Transport",
        "Can we transport 15 tons of merchandise from Casablanca to Marrakech via Highway A3? The shipment needs to arrive by tomorrow morning."
    )
    
    # Scenario 3: Constraint violation detection
    run_scenario(
        3,
        "Morning Peak Time Restriction (Violation Detection)",
        "We need to deliver 18 tons of goods to Casablanca city center at 08:30 AM tomorrow. Is this possible with our current fleet?"
    )
    
    # Scenario 4: Truck maintenance issue
    run_scenario(
        4,
        "Maintenance Issue Consideration",
        "I need to transport 25 tons for a long-distance trip (600 km). What are my options given current truck status?"
    )
    
    # Scenario 5: Peak time management
    run_scenario(
        5,
        "Evening Peak Time - Alternative Routing",
        "Urgent: 12 tons to be delivered to Casablanca at 17:30 today. Can we make it work?"
    )
    
    # Scenario 6: Heavy cargo
    run_scenario(
        6,
        "Heavy Cargo with Special Requirements",
        "We have a 28-ton industrial equipment shipment for Marrakech. Route optimization is critical due to weight constraints."
    )
    
    # Summary
    print_header("DEMO COMPLETE")
    print("""
All scenarios have been executed. This demonstrates:

✓ Multi-agent collaboration (Recherche → Analyse → Validation → Rédaction)
✓ RAG-powered contextual reasoning (accessing fleet, regulations, maintenance data)
✓ Constraint detection and validation
✓ Alternative suggestion generation
✓ Professional response formatting

KEY OBSERVATIONS:
- Each agent builds upon the previous one's output
- RAG retrieves relevant constraints from private knowledge base
- Validation layer catches potential issues and suggests alternatives
- Final response is formatted for direct client communication

For interactive mode, run:
  python main.py
    """)

if __name__ == "__main__":
    main()
