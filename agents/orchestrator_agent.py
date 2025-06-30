## agents/orchestrator_agent.py
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import BaseOutputParser
import json
import re
import os
from .base_agent import BaseAgent

class TaskOutputParser(BaseOutputParser):
    """Parse the orchestrator's output into structured tasks"""
    
    def parse(self, text: str) -> Dict[str, Any]:
        # Extract JSON from the response
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Fallback parsing
        task_type = "unknown"
        if "contact" in text.lower() and "create" in text.lower():
            task_type = "create_contact"
        elif "contact" in text.lower() and "update" in text.lower():
            task_type = "update_contact"
        elif "deal" in text.lower():
            task_type = "manage_deal"
        
        return {
            "task_type": task_type,
            "agent": "hubspot" if task_type != "unknown" else "none",
            "parameters": {},
            "send_notification": True
        }

class OrchestratorAgent(BaseAgent):
    """Global orchestrator agent that delegates tasks to specialized agents"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Set API key in environment if not already there
        if "OPENAI_API_KEY" not in os.environ:
            os.environ["OPENAI_API_KEY"] = config["openai"]["api_key"]
            
        # Initialize with ChatOpenAI from langchain_openai
        self.llm = ChatOpenAI(
            api_key=config["openai"]["api_key"],
            model=config["openai"]["model"],
            temperature=0.1
        )
        self.parser = TaskOutputParser()
        self.prompt_template = ChatPromptTemplate.from_template("""
You are a CRM automation orchestrator. Analyze the user query and determine what CRM operations need to be performed.

User Query: {user_query}

Based on the query, respond with a JSON object containing:
{{
    "task_type": "create_contact|update_contact|create_deal|update_deal",
    "agent": "hubspot",
    "parameters": {{
        // Extract relevant parameters from the query
        "email": "email_if_provided",
        "firstname": "first_name_if_provided",
        "lastname": "last_name_if_provided",
        "company": "company_if_provided",
        "phone": "phone_if_provided",
        "deal_name": "deal_name_if_provided",
        "deal_amount": "amount_if_provided",
        "deal_stage": "stage_if_provided",
        "contact_id": "contact_id_if_updating"
    }},
    "send_notification": true,
    "notification_details": {{
        "recipient": "admin@company.com",
        "subject": "CRM Operation Completed"
    }}
}}

Only include parameters that are actually mentioned or can be inferred from the query.
""")
    
    def execute(self, user_query: str) -> Dict[str, Any]:
        """Analyze user query and create execution plan"""
        try:
            self.log_action("analyze_query", {"query": user_query})
            
            # Create a safer default task plan in case of failure
            default_task = {
                "task_type": "unknown",
                "agent": "none",
                "parameters": {},
                "send_notification": False
            }
            
            try:
                # Generate task plan using LLM
                prompt = self.prompt_template.invoke({"user_query": user_query})
                
                # Use the ChatOpenAI model to get a response
                ai_response = self.llm.invoke(prompt)
                
                # Extract the content from the response
                response_text = ai_response.content if hasattr(ai_response, 'content') else str(ai_response)
                
                # Parse the response
                task_plan = self.parser.parse(response_text)
                
                self.log_action("task_plan_created", task_plan)
            except Exception as e:
                self.logger.error(f"Error generating task plan: {str(e)}")
                task_plan = default_task
            
            return {
                "status": "success",
                "task_plan": task_plan,
                "original_query": user_query
            }
            
        except Exception as e:
            self.logger.error(f"Error in orchestrator: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "task_plan": None
            }
    
    def orchestrate(self, user_query: str) -> Dict[str, Any]:
        """Alias for execute method to match the node name in the workflow"""
        return self.execute(user_query)