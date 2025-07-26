# The MIT License (MIT)
# Copyright © 2025 <kisa134>

import time
import uuid
from pydantic import BaseModel, Field
from typing import Any, Optional

class Task(BaseModel):
    """
    Defines the structure of a task that is sent from a validator to a miner.
    This Pydantic model ensures that all tasks have a consistent format.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "base_task"
    timestamp: float = Field(default_factory=time.time)
    
    # The actual data for the task
    payload: dict = Field(default_factory=dict)
    
    # Response data, to be filled by the miner
    response: Optional[dict] = None

    # Validator signature
    signature: Optional[str] = None

class SquareTask(Task):
    """
    A specific type of task for our demo: squaring a number.
    This demonstrates how the base Task can be extended.
    """
    name: str = "square_task"
    payload: dict # Overriding with a specific structure if needed

if __name__ == "__main__":
    # Example usage
    
    # A validator creates a task
    task_payload = {"number": 10}
    task_to_send = SquareTask(payload=task_payload)
    
    print("--- Task Created by Validator ---")
    print(task_to_send.json(indent=2))
    
    # A miner receives the task, processes it, and adds a response
    received_task = SquareTask(**task_to_send.dict()) # Simulate receiving
    
    number_to_square = received_task.payload.get("number", 0)
    result = number_to_square ** 2
    received_task.response = {"result": result}
    
    print("\n--- Task Processed by Miner ---")
    print(received_task.json(indent=2)) 