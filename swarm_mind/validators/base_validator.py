# The MIT License (MIT)
# Copyright © 2025 <kisa143>

from swarm_mind.neuron import BaseNeuron
from abc import abstractmethod
import asyncio

class BaseValidator(BaseNeuron):
    """
    The base class for all SwarmMind validators.
    Validators are responsible for creating tasks, querying miners,
    evaluating their responses, and setting weights on the network.
    """
    def __init__(self, config=None):
        super().__init__(config=config)
        self.scanned_miners = {} # A dictionary to store discovered miners

    @abstractmethod
    async def query_network(self):
        """
        Scans the network for miners, sends them tasks, and collects results.
        """
        pass

    @abstractmethod
    async def score_responses(self, responses: list):
        """
        Scores the responses from miners and prepares to set weights.
        """
        pass

    async def main_loop_logic(self):
        """
        The main loop for a validator.
        1. Query the network to get responses from miners.
        2. Score the responses.
        3. Set weights on the blockchain (placeholder).
        """
        print(f"[{self.config.neuron.name}] Validator is starting a new evaluation cycle...")
        
        # Step 1: Query miners
        responses = await self.query_network()
        
        # Step 2: Score responses
        if responses:
            await self.score_responses(responses)
        else:
            print(f"[{self.config.neuron.name}] No responses received from miners.")
            
        # Wait for the next cycle
        await asyncio.sleep(30) 