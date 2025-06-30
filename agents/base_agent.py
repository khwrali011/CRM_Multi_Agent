## agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
import logging

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's primary function"""
        pass
    
    def log_action(self, action: str, details: Dict[str, Any]):
        """Log agent actions for debugging and monitoring"""
        self.logger.info(f"Agent: {self.__class__.__name__} | Action: {action} | Details: {details}")
