# The MIT License (MIT)
# Copyright © 2025 <kisa134>

from swarm_mind.neuron import BaseNeuron
from abc import abstractmethod

class BaseMiner(BaseNeuron):
    """
    The base class for all SwarmMind miners.
    Miners are responsible for performing the actual work in the network,
    such as training models or processing data.
    """
    def __init__(self, config=None):
        super().__init__(config=config)

    @abstractmethod
    def forward(self, query: dict) -> dict:
        """
        Defines the primary operation of the miner.
        This method receives a query from a validator, performs a computation,
        and returns a result.

        Args:
            query (dict): The query data sent by a validator.

        Returns:
            dict: The result of the computation.
        """
        pass

    async def main_loop_logic(self):
        """
        The main loop for a miner. This loop will consist of:
        1. Listening for incoming queries from the P2P network.
        2. Processing queries using the `forward` method.
        3. Sending back the results.
        
        (This is a placeholder for now)
        """
        print(f"[{self.config.neuron.name}] Miner is listening for tasks...")
        # In the future, this will be driven by the P2P manager
        pass 