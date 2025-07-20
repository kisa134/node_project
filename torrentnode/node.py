"""
Основной модуль ноды TorrentNode Net

Реализует P2P протокол, управление торрентами, DHT и взаимодействие с пирами.
"""

import asyncio
import json
import logging
import os
import random
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

import aiofiles
import bencodepy
import libtorrent as lt
import structlog
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from pydantic import BaseModel, Field
from rich.console import Console
from rich.table import Table

from .task_executor import TaskExecutor, Task, TaskResult
from .rewards import RewardSystem
from .utils import generate_node_id, create_torrent, verify_hash, get_free_port

# Настройка логирования
logger = structlog.get_logger()
console = Console()


@dataclass
class NodeConfig:
    """Конфигурация ноды"""
    name: str = field(default_factory=lambda: f"node_{random.randint(1000, 9999)}")
    port: int = 8888
    dht_port: int = 8889
    data_dir: Path = Path("./data")
    torrent_dir: Path = Path("./torrents")
    max_peers: int = 50
    max_tasks: int = 5
    enable_dht: bool = True
    enable_encryption: bool = True
    bootstrap_nodes: List[str] = field(default_factory=list)
    upload_rate_limit: int = 0  # 0 = unlimited
    download_rate_limit: int = 0
    log_level: str = "INFO"
    
    def __post_init__(self):
        self.data_dir = Path(self.data_dir)
        self.torrent_dir = Path(self.torrent_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.torrent_dir.mkdir(parents=True, exist_ok=True)


class PeerInfo(BaseModel):
    """Информация о пире"""
    peer_id: str
    address: str
    port: int
    last_seen: float = Field(default_factory=time.time)
    reputation: float = 1.0
    completed_tasks: int = 0
    failed_tasks: int = 0


class Node:
    """Основной класс ноды TorrentNode Net"""
    
    def __init__(self, config: Optional[NodeConfig] = None):
        self.config = config or NodeConfig()
        self.node_id = generate_node_id()
        self.session: Optional[lt.session] = None
        self.peers: Dict[str, PeerInfo] = {}
        self.active_torrents: Dict[str, lt.torrent_handle] = {}
        self.task_executor = TaskExecutor()
        self.reward_system = RewardSystem(str(self.config.data_dir / "tokens.db"))
        self.running = False
        self._setup_logging()
        self._setup_encryption()
        
        # Статистика
        self.stats = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "data_uploaded": 0,
            "data_downloaded": 0,
            "tokens_earned": 0,
            "uptime_start": time.time()
        }
        
        logger.info("Node initialized", node_id=self.node_id, config=self.config)
    
    def _setup_logging(self):
        """Настройка логирования"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _setup_encryption(self):
        """Настройка шифрования"""
        if self.config.enable_encryption:
            # Генерация RSA ключей для ноды
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            self.public_key = self.private_key.public_key()
            
            # Симметричный ключ для быстрого шифрования
            self.fernet = Fernet(Fernet.generate_key())
            
            logger.info("Encryption enabled")
    
    def _create_session(self) -> lt.session:
        """Создание libtorrent сессии"""
        settings = {
            'user_agent': f'TorrentNode/{self.node_id}',
            'listen_interfaces': f'0.0.0.0:{self.config.port}',
            'enable_dht': self.config.enable_dht,
            'enable_lsd': True,
            'enable_upnp': True,
            'enable_natpmp': True,
            'upload_rate_limit': self.config.upload_rate_limit,
            'download_rate_limit': self.config.download_rate_limit,
            'alert_mask': lt.alert.category_t.all_categories,
            'max_allowed_in_request_queue': 2000,
            'max_out_request_queue': 2000,
            'request_timeout': 10,
            'peer_timeout': 20,
        }
        
        session = lt.session(settings)
        
        # Добавление DHT роутеров
        if self.config.enable_dht:
            session.add_dht_router("router.bittorrent.com", 6881)
            session.add_dht_router("router.utorrent.com", 6881)
            session.add_dht_router("dht.transmissionbt.com", 6881)
            
            # Добавление bootstrap нод
            for node in self.config.bootstrap_nodes:
                try:
                    host, port = node.split(':')
                    session.add_dht_node((host, int(port)))
                    logger.info(f"Added bootstrap node: {node}")
                except Exception as e:
                    logger.error(f"Failed to add bootstrap node {node}: {e}")
        
        return session
    
    async def start(self):
        """Запуск ноды"""
        logger.info("Starting node", node_id=self.node_id, port=self.config.port)
        
        # Создание libtorrent сессии
        self.session = self._create_session()
        self.running = True
        
        # Инициализация баланса токенов
        self.reward_system.init_balance(self.node_id)
        
        # Запуск фоновых задач
        tasks = [
            asyncio.create_task(self._handle_alerts()),
            asyncio.create_task(self._process_tasks()),
            asyncio.create_task(self._maintain_peers()),
            asyncio.create_task(self._report_stats()),
        ]
        
        console.print(f"[green]✓ Node {self.node_id} started on port {self.config.port}[/green]")
        
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Node shutting down")
        finally:
            await self.stop()
    
    async def stop(self):
        """Остановка ноды"""
        self.running = False
        if self.session:
            # Сохранение состояния
            self._save_state()
            self.session.pause()
        logger.info("Node stopped", node_id=self.node_id)
    
    async def _handle_alerts(self):
        """Обработка уведомлений от libtorrent"""
        while self.running:
            alerts = self.session.pop_alerts()
            for alert in alerts:
                await self._process_alert(alert)
            await asyncio.sleep(0.1)
    
    async def _process_alert(self, alert):
        """Обработка конкретного уведомления"""
        if isinstance(alert, lt.peer_connect_alert):
            logger.info(f"Peer connected: {alert.endpoint}")
            await self._on_peer_connected(alert)
        
        elif isinstance(alert, lt.torrent_finished_alert):
            logger.info(f"Torrent finished: {alert.torrent_name}")
            await self._on_torrent_finished(alert)
        
        elif isinstance(alert, lt.dht_announce_alert):
            logger.debug(f"DHT announce: {alert.info_hash}")
        
        elif isinstance(alert, lt.piece_finished_alert):
            logger.debug(f"Piece finished: {alert.piece_index}")
            self.stats["data_downloaded"] += alert.piece_size
    
    async def _on_peer_connected(self, alert):
        """Обработка подключения пира"""
        peer_id = str(alert.pid)
        peer_info = PeerInfo(
            peer_id=peer_id,
            address=alert.endpoint[0],
            port=alert.endpoint[1]
        )
        self.peers[peer_id] = peer_info
        logger.info(f"Added peer: {peer_id}")
    
    async def _on_torrent_finished(self, alert):
        """Обработка завершения загрузки торрента"""
        info_hash = str(alert.info_hash)
        if info_hash in self.active_torrents:
            # Извлечение и выполнение задачи
            handle = self.active_torrents[info_hash]
            await self._extract_and_execute_task(handle)
    
    async def _extract_and_execute_task(self, torrent_handle):
        """Извлечение и выполнение задачи из торрента"""
        try:
            # Получение информации о торренте
            info = torrent_handle.torrent_file()
            save_path = torrent_handle.save_path()
            
            # Поиск файла с задачей
            task_file = None
            for file in info.files():
                if file.path.endswith('.json'):
                    task_file = os.path.join(save_path, file.path)
                    break
            
            if not task_file or not os.path.exists(task_file):
                logger.error("Task file not found in torrent")
                return
            
            # Загрузка задачи
            async with aiofiles.open(task_file, 'r') as f:
                task_data = json.loads(await f.read())
            
            # Проверка подписи и хэша
            if self.config.enable_encryption and not self._verify_task_signature(task_data):
                logger.error("Invalid task signature")
                return
            
            # Создание объекта задачи
            task = Task(**task_data)
            
            # Выполнение задачи
            logger.info(f"Executing task: {task.id}")
            result = await self.task_executor.execute(task)
            
            if result.success:
                # Начисление вознаграждения
                self.reward_system.add_reward(self.node_id, task.reward)
                self.stats["tasks_completed"] += 1
                self.stats["tokens_earned"] += task.reward
                logger.info(f"Task completed successfully: {task.id}")
                
                # Отправка результата обратно
                await self._send_result(task, result)
            else:
                self.stats["tasks_failed"] += 1
                logger.error(f"Task failed: {task.id}, error: {result.error}")
            
        except Exception as e:
            logger.error(f"Error processing task: {e}")
            self.stats["tasks_failed"] += 1
    
    async def distribute_task(self, task: Task) -> str:
        """Распределение задачи в сети"""
        logger.info(f"Distributing task: {task.id}")
        
        # Создание директории для задачи
        task_dir = self.config.data_dir / f"task_{task.id}"
        task_dir.mkdir(exist_ok=True)
        
        # Сохранение задачи в JSON
        task_file = task_dir / "task.json"
        task_data = task.dict()
        
        # Добавление подписи если включено шифрование
        if self.config.enable_encryption:
            task_data["signature"] = self._sign_task(task_data)
        
        async with aiofiles.open(task_file, 'w') as f:
            await f.write(json.dumps(task_data, indent=2))
        
        # Создание торрента
        torrent_file = create_torrent(
            str(task_dir),
            f"TorrentNode Task: {task.type}",
            trackers=["udp://tracker.openbittorrent.com:80/announce"]
        )
        
        # Добавление торрента в сессию
        info = lt.torrent_info(torrent_file)
        params = {
            'ti': info,
            'save_path': str(self.config.data_dir),
            'flags': lt.torrent_flags.seed_mode
        }
        
        handle = self.session.add_torrent(params)
        info_hash = str(info.info_hash())
        self.active_torrents[info_hash] = handle
        
        logger.info(f"Task distributed with hash: {info_hash}")
        console.print(f"[green]✓ Task {task.id} distributed[/green]")
        console.print(f"  Hash: {info_hash}")
        console.print(f"  Reward: {task.reward} tokens")
        
        return info_hash
    
    async def wait_for_result(self, torrent_hash: str, timeout: int = 300) -> Optional[Any]:
        """Ожидание результата выполнения задачи"""
        logger.info(f"Waiting for result: {torrent_hash}")
        
        start_time = time.time()
        result_file = self.config.data_dir / f"results/{torrent_hash}.json"
        
        while time.time() - start_time < timeout:
            if result_file.exists():
                async with aiofiles.open(result_file, 'r') as f:
                    result_data = json.loads(await f.read())
                return result_data.get("result")
            
            await asyncio.sleep(1)
        
        logger.warning(f"Timeout waiting for result: {torrent_hash}")
        return None
    
    async def _send_result(self, task: Task, result: TaskResult):
        """Отправка результата выполнения задачи"""
        # В реальной системе здесь была бы отправка через P2P
        # Для демонстрации сохраняем локально
        result_dir = self.config.data_dir / "results"
        result_dir.mkdir(exist_ok=True)
        
        result_file = result_dir / f"{task.id}.json"
        async with aiofiles.open(result_file, 'w') as f:
            await f.write(json.dumps({
                "task_id": task.id,
                "result": result.result,
                "execution_time": result.execution_time,
                "node_id": self.node_id
            }))
    
    async def _process_tasks(self):
        """Фоновая обработка задач"""
        while self.running:
            # Проверка новых торрентов с задачами
            for info_hash, handle in self.active_torrents.items():
                if handle.is_seed():
                    continue
                
                status = handle.status()
                if status.state == lt.torrent_status.seeding:
                    await self._extract_and_execute_task(handle)
            
            await asyncio.sleep(5)
    
    async def _maintain_peers(self):
        """Поддержание списка пиров"""
        while self.running:
            current_time = time.time()
            
            # Удаление неактивных пиров
            inactive_peers = [
                peer_id for peer_id, info in self.peers.items()
                if current_time - info.last_seen > 300  # 5 минут
            ]
            
            for peer_id in inactive_peers:
                del self.peers[peer_id]
                logger.info(f"Removed inactive peer: {peer_id}")
            
            # Поиск новых пиров через DHT
            if self.config.enable_dht and len(self.peers) < self.config.max_peers:
                # В реальной системе здесь был бы DHT lookup
                pass
            
            await asyncio.sleep(30)
    
    async def _report_stats(self):
        """Периодический вывод статистики"""
        while self.running:
            await asyncio.sleep(60)  # Каждую минуту
            
            uptime = int(time.time() - self.stats["uptime_start"])
            balance = self.reward_system.get_balance(self.node_id)
            
            table = Table(title=f"Node {self.node_id} Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Uptime", f"{uptime // 60} minutes")
            table.add_row("Peers", str(len(self.peers)))
            table.add_row("Active Torrents", str(len(self.active_torrents)))
            table.add_row("Tasks Completed", str(self.stats["tasks_completed"]))
            table.add_row("Tasks Failed", str(self.stats["tasks_failed"]))
            table.add_row("Data Uploaded", f"{self.stats['data_uploaded'] / 1024 / 1024:.2f} MB")
            table.add_row("Data Downloaded", f"{self.stats['data_downloaded'] / 1024 / 1024:.2f} MB")
            table.add_row("Token Balance", f"{balance:.2f}")
            table.add_row("Tokens Earned", f"{self.stats['tokens_earned']:.2f}")
            
            console.print(table)
    
    def _sign_task(self, task_data: dict) -> str:
        """Подпись задачи приватным ключом"""
        message = json.dumps(task_data, sort_keys=True).encode()
        signature = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature.hex()
    
    def _verify_task_signature(self, task_data: dict) -> bool:
        """Проверка подписи задачи"""
        if "signature" not in task_data:
            return False
        
        signature = bytes.fromhex(task_data.pop("signature"))
        message = json.dumps(task_data, sort_keys=True).encode()
        
        try:
            # В реальной системе публичный ключ брался бы от отправителя
            self.public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def _save_state(self):
        """Сохранение состояния ноды"""
        state_file = self.config.data_dir / "node_state.json"
        state = {
            "node_id": self.node_id,
            "stats": self.stats,
            "peers": [peer.dict() for peer in self.peers.values()],
            "timestamp": time.time()
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info("Node state saved")
    
    def get_balance(self) -> float:
        """Получение баланса токенов"""
        return self.reward_system.get_balance(self.node_id)


# CLI точка входа
if __name__ == "__main__":
    import click
    
    @click.command()
    @click.option('--port', default=8888, help='Port to listen on')
    @click.option('--name', default=None, help='Node name')
    @click.option('--bootstrap', multiple=True, help='Bootstrap nodes (host:port)')
    @click.option('--verbose', is_flag=True, help='Enable verbose logging')
    def main(port, name, bootstrap, verbose):
        """Run TorrentNode Net node"""
        config = NodeConfig(
            port=port,
            name=name or f"node_{port}",
            bootstrap_nodes=list(bootstrap),
            log_level="DEBUG" if verbose else "INFO"
        )
        
        node = Node(config)
        
        try:
            asyncio.run(node.start())
        except KeyboardInterrupt:
            console.print("\n[yellow]Shutting down...[/yellow]")
    
    main() 