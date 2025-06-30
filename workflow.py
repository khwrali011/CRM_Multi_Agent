## workflow.py
from typing import Dict, Any
from langgraph.graph import Graph, END
from agents.orchestrator_agent import OrchestratorAgent
from agents.hubspot_agent import HubSpotAgent
from agents.email_agent import EmailAgent
import json
import logging

class CRMWorkflow:
    """Main workflow orchestrator using LangGraph"""
    
    def __init__(self, config_path: str = "config.json"):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize agents
        self.orchestrator = OrchestratorAgent(self.config)
        self.hubspot_agent = HubSpotAgent(self.config)
        self.email_agent = EmailAgent(self.config)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Build workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> Graph:
        """Build the LangGraph workflow"""
        
        def orchestrator_node(state: Dict[str, Any]) -> Dict[str, Any]:
            """Orchestrator node - analyzes query and creates task plan"""
            user_query = state["user_query"]
            # Use try/except to handle the function call safely
            try:
                result = self.orchestrator.execute(user_query)
                return {
                    **state,
                    "orchestrator_result": result,
                    "task_plan": result.get("task_plan"),
                    "original_query": user_query
                }
            except Exception as e:
                self.logger.error(f"Error in orchestrator node: {str(e)}")
                return {
                    **state,
                    "error": str(e),
                    "task_plan": None,
                    "original_query": user_query
                }
        
        def hubspot_node(state: Dict[str, Any]) -> Dict[str, Any]:
            """HubSpot node - executes CRM operations"""
            task_plan = state.get("task_plan")
            if not task_plan:
                return {
                    **state,
                    "hubspot_result": {"status": "error", "error": "No task plan available"}
                }
            
            result = self.hubspot_agent.execute(task_plan)
            return {
                **state,
                "hubspot_result": result,
                "operation_result": result
            }
        
        def email_node(state: Dict[str, Any]) -> Dict[str, Any]:
            """Email node - sends notification"""
            task_plan = state.get("task_plan", {})
            operation_result = state.get("operation_result", {})
            original_query = state.get("original_query", "")
            
            if not task_plan.get("send_notification", True):
                return {
                    **state,
                    "email_result": {"status": "skipped", "message": "Notification disabled"}
                }
            
            email_task = {
                "operation_result": operation_result,
                "notification_details": task_plan.get("notification_details", {}),
                "original_query": original_query
            }
            
            result = self.email_agent.execute(email_task)
            return {
                **state,
                "email_result": result
            }
        
        def should_send_email(state: Dict[str, Any]) -> str:
            """Conditional edge - decide whether to send email"""
            task_plan = state.get("task_plan", {})
            hubspot_result = state.get("hubspot_result", {})
            
            # Send email if notification is enabled and HubSpot operation completed
            if task_plan.get("send_notification", True) and hubspot_result.get("status"):
                return "send_email"
            else:
                return "end"
        
        # Build the graph
        workflow = Graph()
        
        # Add nodes
        workflow.add_node("orchestrator", orchestrator_node)
        workflow.add_node("hubspot_operation", hubspot_node)
        workflow.add_node("send_email", email_node)
        
        # Add edges
        workflow.add_edge("orchestrator", "hubspot_operation")
        workflow.add_conditional_edges(
            "hubspot_operation",
            should_send_email,
            {
                "send_email": "send_email",
                "end": END
            }
        )
        workflow.add_edge("send_email", END)
        
        # Set entry point
        workflow.set_entry_point("orchestrator")
        
        # Return the compiled workflow
        return workflow.compile()
    
    def execute(self, user_query: str) -> Dict[str, Any]:
        """Execute the complete workflow"""
        try:
            self.logger.info(f"Starting workflow for query: {user_query}")
            
            # Initialize state
            initial_state = {"user_query": user_query}
            
            # Execute workflow
            try:
                final_state = self.workflow.invoke(initial_state)
            except AttributeError:
                # Handle case where workflow.invoke is not available
                # Retry with newer LangGraph API
                from langgraph.graph import StateGraph
                if isinstance(self.workflow, StateGraph):
                    final_state = self.workflow.run(initial_state)
                else:
                    raise ValueError("Workflow graph is not properly compiled or initialized")
            
            # Prepare response
            response = {
                "status": "completed",
                "original_query": user_query,
                "task_plan": final_state.get("task_plan"),
                "hubspot_result": final_state.get("hubspot_result"),
                "email_result": final_state.get("email_result"),
                "workflow_successful": self._is_workflow_successful(final_state)
            }
            
            self.logger.info(f"Workflow completed: {response['workflow_successful']}")
            return response
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "original_query": user_query
            }
    
    def _is_workflow_successful(self, state: Dict[str, Any]) -> bool:
        """Check if the overall workflow was successful"""
        hubspot_result = state.get("hubspot_result", {})
        return hubspot_result.get("status") == "success"
