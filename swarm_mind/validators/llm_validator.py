# The MIT License (MIT)
# Copyright © 2025 <kisa134>

import asyncio
import json
import requests
from swarm_mind.validators.base_validator import BaseValidator
from swarm_mind.task import SquareTask

class LLMValidator(BaseValidator):
    """
    A validator that uses Ollama (local LLM server) to generate tasks.
    This gives our swarm a much more powerful brain than distilgpt2.
    """
    def __init__(self, config=None):
        super().__init__(config=config)
        print(f"[{self.config.neuron.name}] Initializing Ollama LLM Task Generator...")
        
        # Ollama API settings
        # Use appropriate URL based on environment
        import os
        import socket
        
        # Check if we're in Docker by trying to resolve host.docker.internal
        try:
            socket.gethostbyname('host.docker.internal')
            self.ollama_base_url = "http://host.docker.internal:11434"
            print(f"[{self.config.neuron.name}] Using Docker host connection")
        except socket.gaierror:
            # Try to connect to host network from container
            try:
                # In Docker with --network=host
                socket.create_connection(('localhost', 11434), timeout=1).close()
                self.ollama_base_url = "http://localhost:11434"
                print(f"[{self.config.neuron.name}] Using localhost connection")
            except (ConnectionRefusedError, OSError):
                # Use Docker host IP 
                self.ollama_base_url = "http://172.17.0.1:11434"
                print(f"[{self.config.neuron.name}] Using Docker bridge network")
        except Exception:
            self.ollama_base_url = "http://localhost:11434"
        self.model_name = "llama3:latest"  # Using Llama3 - good balance of power and instruction following
        
        # Test connection to Ollama
        try:
            response = requests.get(f"{self.ollama_base_url}/api/version", timeout=5)
            if response.status_code == 200:
                print(f"[{self.config.neuron.name}] Connected to Ollama {response.json().get('version')}")
            else:
                print(f"[{self.config.neuron.name}] Warning: Ollama responded with status {response.status_code}")
        except Exception as e:
            print(f"[{self.config.neuron.name}] Warning: Could not connect to Ollama: {e}")
            print(f"[{self.config.neuron.name}] Will attempt to use Ollama anyway...")
        
        print(f"[{self.config.neuron.name}] Ollama LLM Task Generator initialized.")

    def generate_with_ollama(self, prompt: str) -> str:
        """
        Sends a prompt to Ollama and returns the response.
        """
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 100
                }
            }
            
            response = requests.post(
                f"{self.ollama_base_url}/api/generate", 
                json=payload, 
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                print(f"[{self.config.neuron.name}] Ollama API error: {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"[{self.config.neuron.name}] Error calling Ollama: {e}")
            return ""

    async def query_network(self):
        """
        Generates a task using Ollama and then (for now) simulates sending it.
        """
        print(f"[{self.config.neuron.name}] Asking Ollama LLM to generate a new task...")
        
        prompt = """Generate ONLY a JSON object to square a number:
{"number": 42}

Replace 42 with any integer between 1-100. Output ONLY the JSON, no thinking, no explanations."""

        try:
            llm_response = self.generate_with_ollama(prompt)
            print(f"[{self.config.neuron.name}] Raw Ollama response: {llm_response[:200]}...")
            
            if not llm_response:
                print(f"[{self.config.neuron.name}] Empty response from Ollama, using fallback")
                raise Exception("Empty Ollama response")
            
            # Extract JSON from response (handle DeepSeek thinking tags)
            import re
            json_match = re.search(r'\{[^}]*"number"[^}]*\}', llm_response)
            if json_match:
                json_str = json_match.group()
                task_payload = json.loads(json_str)
                print(f"[{self.config.neuron.name}] Ollama generated task payload: {task_payload}")
            else:
                raise Exception("No valid JSON found in response")
            
            # Create and simulate task
            task = SquareTask(payload=task_payload)
            print(f"[{self.config.neuron.name}] Created task: {task.id} with payload {task.payload}")
            
            # --- P2P SEND LOGIC WILL GO HERE ---
            # For now, we simulate a response
            simulated_response = self.simulate_miner_response(task)
            return [simulated_response]

        except Exception as e:
            print(f"[{self.config.neuron.name}] Error during Ollama task generation: {e}")
            # Fallback to a default task if Ollama fails
            print(f"[{self.config.neuron.name}] Using fallback task")
            task = SquareTask(payload={"number": 42})
            simulated_response = self.simulate_miner_response(task)
            return [simulated_response]

    def simulate_miner_response(self, task: SquareTask) -> dict:
        """Simulates a miner correctly performing the task."""
        number = task.payload.get("number", 0)
        result = number ** 2
        task.response = {"result": result}
        return task.dict() # Return the full task object with the response

    async def score_responses(self, responses: list):
        """
        Scores the simulated responses.
        """
        for response_data in responses:
            task = SquareTask(**response_data)
            number = task.payload.get("number", 0)
            expected_result = number ** 2
            actual_result = task.response.get("result")

            if actual_result == expected_result:
                print(f"[{self.config.neuron.name}] Scoring response for task {task.id}: Correct! ({actual_result} == {expected_result}) Score: 1.0")
            else:
                print(f"[{self.config.neuron.name}] Scoring response for task {task.id}: Incorrect! ({actual_result} != {expected_result}) Score: 0.0") 