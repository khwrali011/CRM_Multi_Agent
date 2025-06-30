## agents/hubspot_agent.py
import requests
from typing import Dict, Any, Optional
from .base_agent import BaseAgent

class HubSpotAgent(BaseAgent):
    """Agent for managing HubSpot CRM operations"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config["hubspot"]["api_key"]
        self.base_url = config["hubspot"]["base_url"]
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HubSpot CRM operations"""
        task_type = task.get("task_type")
        parameters = task.get("parameters", {})
        
        try:
            if task_type == "create_contact":
                return self.create_contact(parameters)
            elif task_type == "update_contact":
                return self.update_contact(parameters)
            elif task_type == "create_deal":
                return self.create_deal(parameters)
            elif task_type == "update_deal":
                return self.update_deal(parameters)
            else:
                return {"status": "error", "error": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            self.logger.error(f"HubSpot operation failed: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def create_contact(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contact in HubSpot"""
        url = f"{self.base_url}/crm/v3/objects/contacts"
        
        properties = {}
        if parameters.get("email"):
            properties["email"] = parameters["email"]
        if parameters.get("firstname"):
            properties["firstname"] = parameters["firstname"]
        if parameters.get("lastname"):
            properties["lastname"] = parameters["lastname"]
        if parameters.get("company"):
            properties["company"] = parameters["company"]
        if parameters.get("phone"):
            properties["phone"] = parameters["phone"]
        
        payload = {"properties": properties}
        
        self.log_action("create_contact", {"properties": properties})
        
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code == 201:
            contact_data = response.json()
            return {
                "status": "success",
                "operation": "create_contact",
                "contact_id": contact_data.get("id"),
                "data": contact_data
            }
        else:
            return {
                "status": "error",
                "operation": "create_contact",
                "error": response.text
            }
    
    def update_contact(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing contact in HubSpot"""
        contact_id = parameters.get("contact_id")
        if not contact_id:
            return {"status": "error", "error": "Contact ID required for update"}
        
        url = f"{self.base_url}/crm/v3/objects/contacts/{contact_id}"
        
        properties = {}
        if parameters.get("email"):
            properties["email"] = parameters["email"]
        if parameters.get("firstname"):
            properties["firstname"] = parameters["firstname"]
        if parameters.get("lastname"):
            properties["lastname"] = parameters["lastname"]
        if parameters.get("company"):
            properties["company"] = parameters["company"]
        if parameters.get("phone"):
            properties["phone"] = parameters["phone"]
        
        payload = {"properties": properties}
        
        self.log_action("update_contact", {"contact_id": contact_id, "properties": properties})
        
        response = requests.patch(url, headers=self.headers, json=payload)
        
        if response.status_code == 200:
            contact_data = response.json()
            return {
                "status": "success",
                "operation": "update_contact",
                "contact_id": contact_id,
                "data": contact_data
            }
        else:
            return {
                "status": "error",
                "operation": "update_contact",
                "error": response.text
            }
    
    def create_deal(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new deal in HubSpot"""
        url = f"{self.base_url}/crm/v3/objects/deals"
        
        properties = {}
        if parameters.get("deal_name"):
            properties["dealname"] = parameters["deal_name"]
        if parameters.get("deal_amount"):
            properties["amount"] = str(parameters["deal_amount"])
        if parameters.get("deal_stage"):
            properties["dealstage"] = parameters["deal_stage"]
        if parameters.get("pipeline"):
            properties["pipeline"] = parameters["pipeline"]
        
        payload = {"properties": properties}
        
        self.log_action("create_deal", {"properties": properties})
        
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code == 201:
            deal_data = response.json()
            return {
                "status": "success",
                "operation": "create_deal",
                "deal_id": deal_data.get("id"),
                "data": deal_data
            }
        else:
            return {
                "status": "error",
                "operation": "create_deal",
                "error": response.text
            }
    
    def update_deal(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing deal in HubSpot"""
        deal_id = parameters.get("deal_id")
        if not deal_id:
            return {"status": "error", "error": "Deal ID required for update"}
        
        url = f"{self.base_url}/crm/v3/objects/deals/{deal_id}"
        
        properties = {}
        if parameters.get("deal_name"):
            properties["dealname"] = parameters["deal_name"]
        if parameters.get("deal_amount"):
            properties["amount"] = str(parameters["deal_amount"])
        if parameters.get("deal_stage"):
            properties["dealstage"] = parameters["deal_stage"]
        
        payload = {"properties": properties}
        
        self.log_action("update_deal", {"deal_id": deal_id, "properties": properties})
        
        response = requests.patch(url, headers=self.headers, json=payload)
        
        if response.status_code == 200:
            deal_data = response.json()
            return {
                "status": "success",
                "operation": "update_deal",
                "deal_id": deal_id,
                "data": deal_data
            }
        else:
            return {
                "status": "error",
                "operation": "update_deal",
                "error": response.text
            }
