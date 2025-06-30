# CRM Agent

An intelligent automation system for managing customer relationship tasks using AI agents and LangGraph workflows.

## Overview

CRM Agent is a powerful tool that automates common CRM operations through natural language processing. The system interprets user requests, executes corresponding actions in HubSpot CRM, and can send email notifications about completed operations.

## Features

- **Natural Language Interface**: Interact with your CRM using plain English commands
- **HubSpot Integration**: Create and update contacts and deals in HubSpot
- **Automated Email Notifications**: Send customizable notifications when CRM operations complete
- **Extensible Architecture**: Built with LangGraph for maintainable agent-based workflows

## Architecture

The system consists of three specialized AI agents:

1. **Orchestrator Agent**: Analyzes user queries and creates detailed task plans
2. **HubSpot Agent**: Executes CRM operations based on task plans
3. **Email Agent**: Sends notifications about completed operations

## Installation

1. Clone the repository
2. Install requirements:
   ```
   pip install -r requirements.txt
   ```
3. Configure your API keys in `config.json`

## Configuration

Update the `config.json` file with your API keys and configuration:

```json
{
  "hubspot_api_key": "YOUR_HUBSPOT_API_KEY",
  "email_service": {
    "provider": "smtp",
    "smtp_host": "smtp.example.com",
    "smtp_port": 587,
    "username": "your_email@example.com",
    "password": "your_email_password"
  }
}
```

## Usage

Run the main script:

```
python main.py
```

### Example Requests

- "Create a new contact with email john.doe@example.com, name John Doe, and company ABC Corp"
- "Update contact ID 12345 with phone number +1-555-0123"
- "Create a deal called 'Q4 Enterprise Sale' worth $50000 in prospecting stage"
- "Update deal 67890 to closed won stage with amount $75000"

## Project Structure

- `main.py`: Entry point and command-line interface
- `workflow.py`: LangGraph workflow orchestration
- `/agents`: Agent implementations
  - `orchestrator_agent.py`: Query analysis and task planning
  - `hubspot_agent.py`: HubSpot CRM operations
  - `email_agent.py`: Email notification handling
  - `base_agent.py`: Common agent functionality

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
