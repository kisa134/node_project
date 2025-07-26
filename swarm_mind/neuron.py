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

import time
import asyncio
import argparse
from abc import ABC, abstractmethod
from swarm_mind.p2p import P2PManager

class BaseNeuron(ABC):
    """
    The base class for all SwarmMind neurons (miners and validators).
    This class handles the core functionality of a neuron, such as configuration,
    logging, and the main run loop.
    """

    def __init__(self, config=None):
        self.config = self.create_config(config)
        self.running = True
        self.p2p_manager = P2PManager(port=self.config.neuron.p2p_port)
        self.background_tasks = []

    @classmethod
    def create_config(cls, config=None):
        """
        Parses command line arguments and returns a nested configuration object.
        """
        if config is None:
            config = argparse.Namespace() # Start with an empty namespace

        parser = argparse.ArgumentParser()
        cls.add_args(parser)
        
        # Get the default values from the parser
        defaults = parser.parse_args([])
        
        # Create a nested structure for defaults
        nested_defaults = argparse.Namespace()
        for key, value in vars(defaults).items():
            parts = key.split('.')
            d = nested_defaults
            for part in parts[:-1]:
                if not hasattr(d, part):
                    setattr(d, part, argparse.Namespace())
                d = getattr(d, part)
            setattr(d, parts[-1], value)

        # Merge defaults with any provided config
        config = cls.merge_configs(nested_defaults, config)
        
        # Parse command-line arguments to override defaults and config
        parsed_args = parser.parse_args()
        parsed_config = argparse.Namespace()
        for key, value in vars(parsed_args).items():
            parts = key.split('.')
            d = parsed_config
            for part in parts[:-1]:
                if not hasattr(d, part):
                    setattr(d, part, argparse.Namespace())
                d = getattr(d, part)
            setattr(d, parts[-1], value)

        return cls.merge_configs(config, parsed_config)

    @staticmethod
    def merge_configs(base, override):
        """Recursively merges two argparse.Namespace objects."""
        for key, value in vars(override).items():
            if isinstance(value, argparse.Namespace):
                base_value = getattr(base, key, argparse.Namespace())
                setattr(base, key, BaseNeuron.merge_configs(base_value, value))
            else:
                setattr(base, key, value)
        return base

    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser):
        """
        Adds neuron-specific arguments to the command line parser.
        """
        parser.add_argument('--neuron.name', type=str, default='base_neuron', help='Name of the neuron.')
        parser.add_argument('--neuron.log_level', type=str, default='INFO', help='Logging level.')
        parser.add_argument('--neuron.p2p_port', type=int, default=6881, help='Port for P2P communication.')

    async def run(self):
        """
        The main run loop for the neuron. This method should be overridden by subclasses.
        """
        print(f"[{self.config.neuron.name}] Starting base neuron run loop.")
        
        # Start P2P manager
        self.p2p_manager.start()
        if not self.p2p_manager.running:
            print(f"[{self.config.neuron.name}] Failed to start P2P manager. Shutting down.")
            return

        # Start background tasks
        listen_task = asyncio.create_task(self.p2p_manager.listen_for_alerts())
        self.background_tasks.append(listen_task)

        while self.running:
            try:
                await self.main_loop_logic()
            except KeyboardInterrupt:
                print(f"[{self.config.neuron.name}] Interrupted. Shutting down...")
                self.running = False
            except Exception as e:
                print(f"[{self.config.neuron.name}] Error in main loop: {e}")
            
            await asyncio.sleep(1)
        
        # Cleanup
        self.stop()

    @abstractmethod
    async def main_loop_logic(self):
        """

        The main logic of the neuron, to be implemented by subclasses.
        This method is called repeatedly by the run loop.
        """
        pass

    def stop(self):
        """
        Stops the neuron's run loop and all background tasks.
        """
        print(f"[{self.config.neuron.name}] Stopping neuron...")
        self.running = False
        for task in self.background_tasks:
            task.cancel()
        self.p2p_manager.stop()
        print(f"[{self.config.neuron.name}] Neuron stopped.")


if __name__ == "__main__":
    # This is a simple example of how a subclass might work
    class MyNeuron(BaseNeuron):
        @classmethod
        def add_args(cls, parser: argparse.ArgumentParser):
            super().add_args(parser)
            parser.add_argument('--my_neuron.value', type=int, default=10, help='A custom value for this neuron.')

        async def main_loop_logic(self):
            # The heartbeat is now replaced by the P2P alert listener logs
            await asyncio.sleep(5)

    my_neuron = MyNeuron()
    asyncio.run(my_neuron.run()) 