# The MIT License (MIT)
# Copyright © 2025 <kisa134>

import asyncio
import libtorrent as lt
from typing import Optional
import bencodepy
import time
import hashlib

# --- Constants for DHT ---
# We use a specific salt for our application to avoid interfering with other DHT users
DHT_SALT = b"swarm_mind_dht_salt"

class P2PManager:
    """
    Handles the peer-to-peer communication layer for a neuron using libtorrent.
    This class manages the libtorrent session, DHT, and torrenting of tasks.
    """
    def __init__(self, port: int = 6881, bootstrap_nodes: list = None):
        self.port = port
        self.bootstrap_nodes = bootstrap_nodes or [
            "router.utorrent.com:6881",
            "router.bittorrent.com:6881",
            "dht.transmissionbt.com:6881",
        ]
        self.session: Optional[lt.session] = None
        self.running = False
        self.pending_get_requests = {}

    def start(self):
        """
        Initializes and starts the libtorrent session.
        """
        print(f"[P2P] Starting session on port {self.port}...")
        try:
            settings = {
                'listen_interfaces': f'0.0.0.0:{self.port}',
                'enable_dht': True,
                'alert_mask': lt.alert.category_t.all_categories,
                'dht_bootstrap_nodes': ','.join(self.bootstrap_nodes),
            }
            self.session = lt.session(settings)
            
            # Apply additional settings separately (DHT settings are built-in)
            additional_settings = {}
            self.session.apply_settings(additional_settings)

            # Add DHT bootstrap nodes
            for node in self.bootstrap_nodes:
                host, port_str = node.split(':')
                self.session.add_dht_router(host, int(port_str))
            
            print("[P2P] Session started successfully.")
            self.running = True
        except Exception as e:
            print(f"[P2P] Error starting session: {e}")
            self.session = None

    async def listen_for_alerts(self):
        """
        An asynchronous loop to listen for and handle alerts from libtorrent.
        """
        if not self.session:
            return

        print("[P2P] Listening for alerts...")
        while self.running:
            self.session.post_dht_stats()
            alerts = self.session.pop_alerts()
            for alert in alerts:
                if isinstance(alert, lt.dht_stats_alert):
                    if alert.total_nodes > 0:
                        print(f"[P2P] DHT Stats: {alert.total_nodes} nodes.")
                elif isinstance(alert, lt.dht_put_alert):
                    self.handle_dht_put(alert)
                elif isinstance(alert, lt.dht_mutable_item_alert):
                    self.handle_dht_get(alert)
                # Here you can handle other alerts, e.g., for incoming tasks
            
            await asyncio.sleep(2) # Check for alerts every 2 seconds

    def dht_put(self, key: bytes, data: dict) -> asyncio.Future:
        """
        Stores a mutable item in the DHT.
        'key' should be a 32-byte Ed25519 public key.
        """
        future = asyncio.Future()
        bencoded_data = bencodepy.encode(data)
        
        # For simplicity, we use the key as both the public and secret key part.
        # In a real system, you'd use a proper keypair.
        self.session.dht_put_item(key, DHT_SALT, bencoded_data, key)
        self.pending_get_requests[key] = future # Use key to track this put op
        return future

    def dht_get(self, key: bytes) -> asyncio.Future:
        """
        Retrieves a mutable item from the DHT.
        'key' should be the 32-byte Ed25519 public key the data was stored under.
        """
        future = asyncio.Future()
        self.session.dht_get_item(key, DHT_SALT)
        self.pending_get_requests[key] = future
        return future

    def handle_dht_put(self, alert: lt.dht_put_alert):
        """Handles the response from a dht_put operation."""
        key = alert.public_key
        if key in self.pending_get_requests:
            future = self.pending_get_requests.pop(key)
            if not future.done():
                if alert.error:
                    future.set_exception(RuntimeError(f"DHT put failed: {alert.error.message()}"))
                else:
                    future.set_result(True)
    
    def handle_dht_get(self, alert: lt.dht_mutable_item_alert):
        """Handles the response from a dht_get operation."""
        key = alert.public_key
        if key in self.pending_get_requests:
            future = self.pending_get_requests.pop(key)
            if not future.done():
                if alert.item:
                    try:
                        value = bencodepy.decode(alert.item.value())
                        future.set_result(value)
                    except Exception as e:
                        future.set_exception(RuntimeError(f"Failed to decode DHT item: {e}"))
                else:
                    future.set_result(None) # Not found

    def stop(self):
        """
        Stops the libtorrent session.
        """
        if self.session:
            print("[P2P] Stopping session...")
            self.running = False
            # In a real application, you might want to save session state here
            self.session = None
            print("[P2P] Session stopped.")

if __name__ == '__main__':
    # Example usage
    async def main():
        p2p_manager = P2PManager()
        p2p_manager.start()
        
        if p2p_manager.running:
            # --- Test DHT Put/Get ---
            test_key = hashlib.sha256(b"my_test_key").digest()
            test_data = {"message": "hello swarm", "timestamp": time.time()}
            
            print(f"\n[Test] Storing data in DHT with key: {test_key.hex()}")
            put_future = p2p_manager.dht_put(test_key, test_data)
            put_success = await put_future
            print(f"[Test] DHT Put successful: {put_success}")
            
            print(f"\n[Test] Retrieving data from DHT...")
            get_future = p2p_manager.dht_get(test_key)
            retrieved_data = await get_future
            print(f"[Test] Retrieved data: {retrieved_data}")

            listen_task = asyncio.create_task(p2p_manager.listen_for_alerts())
            
            try:
                # Run for a short period for demonstration
                await asyncio.sleep(10)
            finally:
                listen_task.cancel()
                p2p_manager.stop()

    asyncio.run(main()) 