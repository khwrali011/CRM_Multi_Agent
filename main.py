## main.py
from workflow import CRMWorkflow
import json

def main():
    """Main entry point for the CRM automation system"""
    
    # Initialize workflow
    workflow = CRMWorkflow()
    
    print("🤖 CRM Automation System Started")
    print("=" * 50)
    
    while True:
        try:
            # Get user input
            user_query = input("\nEnter your CRM request (or 'quit' to exit): ").strip()
            
            if user_query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_query:
                print("Please enter a valid request.")
                continue
            
            print(f"\n🔄 Processing: {user_query}")
            
            # Execute workflow
            result = workflow.execute(user_query)
            
            # Display results
            print("\n" + "=" * 50)
            print("📊 WORKFLOW RESULTS")
            print("=" * 50)
            
            if result["status"] == "completed":
                print(f"✅ Status: {result['workflow_successful'] and 'SUCCESS' or 'PARTIAL'}")
                
                # Show task plan
                if result.get("task_plan"):
                    task_plan = result["task_plan"]
                    print(f"📋 Task: {task_plan.get('task_type', 'Unknown').replace('_', ' ').title()}")
                
                # Show HubSpot result
                hubspot_result = result.get("hubspot_result", {})
                if hubspot_result.get("status") == "success":
                    print(f"🎯 HubSpot: Operation completed successfully")
                    if hubspot_result.get("contact_id"):
                        print(f"   └─ Contact ID: {hubspot_result['contact_id']}")
                    if hubspot_result.get("deal_id"):
                        print(f"   └─ Deal ID: {hubspot_result['deal_id']}")
                else:
                    print(f"❌ HubSpot: {hubspot_result.get('error', 'Operation failed')}")
                
                # Show email result
                email_result = result.get("email_result", {})
                if email_result.get("status") == "success":
                    print(f"📧 Email: Notification sent successfully")
                elif email_result.get("status") == "skipped":
                    print(f"📧 Email: Notification skipped")
                else:
                    print(f"❌ Email: {email_result.get('error', 'Failed to send')}")
            
            else:
                print(f"❌ Status: FAILED")
                print(f"Error: {result.get('error', 'Unknown error')}")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()

## Example usage scenarios:

def demo_scenarios():
    """Demonstration of various use cases"""
    
    workflow = CRMWorkflow()
    
    scenarios = [
        "Create a new contact with email john.doe@example.com, name John Doe, and company ABC Corp",
        "Update contact ID 12345 with phone number +1-555-0123",
        "Create a deal called 'Q4 Enterprise Sale' worth $50000 in prospecting stage",
        "Update deal 67890 to closed won stage with amount $75000"
    ]
    
    for scenario in scenarios:
        print(f"\n🧪 Testing scenario: {scenario}")
        result = workflow.execute(scenario)
        print(f"Result: {result['workflow_successful'] and 'SUCCESS' or 'FAILED'}")