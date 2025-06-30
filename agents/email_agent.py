## agents/email_agent.py
import requests
from typing import Dict, Any
from .base_agent import BaseAgent

class EmailAgent(BaseAgent):
    """Agent for sending email notifications using Elastic Email"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config["elastic_email"]["api_key"]
        self.base_url = config["elastic_email"]["base_url"]
        self.from_email = config["notification_email"]["from_email"]
        self.from_name = config["notification_email"]["from_name"]
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Send email notification"""
        try:
            # Extract notification details
            operation_result = task.get("operation_result", {})
            notification_details = task.get("notification_details", {})
            
            # Prepare email content
            subject = self._generate_subject(operation_result)
            body = self._generate_body(operation_result, task.get("original_query", ""))
            
            # Default recipient
            recipient = notification_details.get("recipient", "admin@company.com")
            
            return self.send_email(recipient, subject, body)
            
        except Exception as e:
            self.logger.error(f"Email sending failed: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def send_email(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """Send email using Elastic Email API"""
        url = f"{self.base_url}/email/send"
        
        payload = {
            "apikey": self.api_key,
            "from": self.from_email,
            "fromName": self.from_name,
            "to": to_email,
            "subject": subject,
            "bodyHtml": body,
            "isTransactional": True
        }
        
        self.log_action("send_email", {"to": to_email, "subject": subject})
        
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return {
                    "status": "success",
                    "operation": "send_email",
                    "message_id": result.get("data", {}).get("messageid"),
                    "recipient": to_email
                }
            else:
                return {
                    "status": "error",
                    "operation": "send_email",
                    "error": result.get("error", "Unknown error")
                }
        else:
            return {
                "status": "error",
                "operation": "send_email",
                "error": f"HTTP {response.status_code}: {response.text}"
            }
    
    def _generate_subject(self, operation_result: Dict[str, Any]) -> str:
        """Generate email subject based on operation result"""
        operation = operation_result.get("operation", "CRM Operation")
        status = operation_result.get("status", "unknown")
        
        if status == "success":
            return f"✅ CRM Operation Successful: {operation.replace('_', ' ').title()}"
        else:
            return f"❌ CRM Operation Failed: {operation.replace('_', ' ').title()}"
    
    def _generate_body(self, operation_result: Dict[str, Any], original_query: str) -> str:
        """Generate email body with operation details"""
        operation = operation_result.get("operation", "Unknown")
        status = operation_result.get("status", "unknown")
        
        if status == "success":
            body = f"""
            <html>
            <body>
                <h2>CRM Operation Completed Successfully</h2>
                <p><strong>Original Request:</strong> {original_query}</p>
                <p><strong>Operation:</strong> {operation.replace('_', ' ').title()}</p>
                <p><strong>Status:</strong> ✅ Success</p>
                
                <h3>Operation Details:</h3>
                <ul>
            """
            
            if operation_result.get("contact_id"):
                body += f"<li><strong>Contact ID:</strong> {operation_result['contact_id']}</li>"
            if operation_result.get("deal_id"):
                body += f"<li><strong>Deal ID:</strong> {operation_result['deal_id']}</li>"
            
            body += """
                </ul>
                <p><em>This is an automated notification from the CRM Automation System.</em></p>
            </body>
            </html>
            """
        else:
            body = f"""
            <html>
            <body>
                <h2>CRM Operation Failed</h2>
                <p><strong>Original Request:</strong> {original_query}</p>
                <p><strong>Operation:</strong> {operation.replace('_', ' ').title()}</p>
                <p><strong>Status:</strong> ❌ Failed</p>
                <p><strong>Error:</strong> {operation_result.get('error', 'Unknown error')}</p>
                
                <p><em>Please check the system logs for more details.</em></p>
            </body>
            </html>
            """
        
        return body