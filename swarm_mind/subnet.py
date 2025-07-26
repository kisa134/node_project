# The MIT License (MIT)
# Copyright © 2025 <kisa134>

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT of OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import torch
from abc import ABC, abstractmethod

class BaseSubnet(ABC):
    """
    The base class for all SwarmMind subnets.
    A subnet defines the specific problem domain that miners and validators
    in the network are working on. It includes the logic for reward calculation,
    task validation, and setting weights.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def reward(self, query: torch.Tensor, response: torch.Tensor) -> float:
        """
        Calculates the reward for a given query and response.
        This method must be implemented by subclasses.
        
        Args:
            query (torch.Tensor): The input query tensor.
            response (torch.Tensor): The response tensor from a miner.
            
        Returns:
            float: The calculated reward.
        """
        pass

    @abstractmethod
    def forward_pass(self, query: torch.Tensor):
        """
        Defines the forward pass logic for the subnet.
        This could involve calling miners, processing their responses, etc.
        """
        pass

    @abstractmethod
    def set_weights(self):
        """
        Sets the weights for miners in the subnet based on their performance.
        This is a core part of the consensus mechanism.
        """
        pass

# Example of a simple subnet for a regression task
class RegressionSubnet(BaseSubnet):
    
    def __init__(self):
        super().__init__(name="RegressionSubnet", description="A subnet for simple regression tasks.")

    def reward(self, query: torch.Tensor, response: torch.Tensor) -> float:
        """
        Reward is based on the negative mean squared error.
        Higher (less negative) is better.
        """
        # For this example, let's assume the query is the target and response is the prediction
        mse = torch.mean((query - response) ** 2)
        return -mse.item()

    def forward_pass(self, query: torch.Tensor):
        print(f"[{self.name}] Performing forward pass with query: {query}")
        # In a real scenario, this would involve sending the query to miners
        # and collecting their responses.
        pass
    
    def set_weights(self):
        print(f"[{self.name}] Setting weights for miners.")
        # Logic to evaluate miner performance and set weights on the blockchain
        pass

if __name__ == "__main__":
    # Example usage
    subnet = RegressionSubnet()
    print(f"Created subnet: {subnet.name} - {subnet.description}")

    # Simulate a query and a response
    target = torch.tensor([1.0, 2.0, 3.0])
    prediction = torch.tensor([1.1, 2.2, 2.9])

    # Calculate reward
    reward_value = subnet.reward(target, prediction)
    print(f"Calculated reward for the response: {reward_value:.4f}")
    
    subnet.forward_pass(target)
    subnet.set_weights() 