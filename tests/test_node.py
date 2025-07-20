"""
Тесты для модуля Node
"""

import asyncio
import json
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import libtorrent as lt

from torrentnode.node import Node, NodeConfig, PeerInfo
from torrentnode.task_executor import Task, TaskType
from torrentnode.utils import generate_node_id, create_torrent


@pytest.fixture
def temp_dir():
    """Временная директория для тестов"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def node_config(temp_dir):
    """Конфигурация ноды для тестов"""
    return NodeConfig(
        name="test_node",
        port=18888,
        dht_port=18889,
        data_dir=temp_dir / "data",
        torrent_dir=temp_dir / "torrents",
        enable_dht=False,  # Отключаем DHT для тестов
        enable_encryption=True,
        log_level="DEBUG"
    )


@pytest.fixture
def node(node_config):
    """Инстанс ноды для тестов"""
    return Node(node_config)


class TestNodeConfig:
    """Тесты для NodeConfig"""
    
    def test_default_config(self):
        """Тест конфигурации по умолчанию"""
        config = NodeConfig()
        assert config.port == 8888
        assert config.dht_port == 8889
        assert config.max_peers == 50
        assert config.max_tasks == 5
        assert config.enable_dht is True
        assert config.enable_encryption is True
    
    def test_custom_config(self, temp_dir):
        """Тест кастомной конфигурации"""
        config = NodeConfig(
            name="custom_node",
            port=9999,
            data_dir=temp_dir / "custom_data",
            max_peers=100,
            enable_dht=False
        )
        assert config.name == "custom_node"
        assert config.port == 9999
        assert config.max_peers == 100
        assert config.enable_dht is False
        assert config.data_dir.exists()
    
    def test_directories_creation(self, temp_dir):
        """Тест создания директорий"""
        config = NodeConfig(
            data_dir=temp_dir / "test_data",
            torrent_dir=temp_dir / "test_torrents"
        )
        assert config.data_dir.exists()
        assert config.torrent_dir.exists()


class TestNode:
    """Тесты для класса Node"""
    
    def test_node_initialization(self, node):
        """Тест инициализации ноды"""
        assert node.node_id.startswith("node_")
        assert node.session is None
        assert len(node.peers) == 0
        assert len(node.active_torrents) == 0
        assert node.running is False
    
    def test_encryption_setup(self, node):
        """Тест настройки шифрования"""
        assert hasattr(node, 'private_key')
        assert hasattr(node, 'public_key')
        assert hasattr(node, 'fernet')
    
    @pytest.mark.asyncio
    async def test_node_start_stop(self, node):
        """Тест запуска и остановки ноды"""
        # Мокаем создание сессии
        with patch.object(node, '_create_session', return_value=MagicMock()):
            # Запускаем ноду на короткое время
            start_task = asyncio.create_task(node.start())
            await asyncio.sleep(0.1)
            
            assert node.running is True
            assert node.session is not None
            
            # Останавливаем ноду
            await node.stop()
            assert node.running is False
            
            # Отменяем задачу запуска
            start_task.cancel()
            try:
                await start_task
            except asyncio.CancelledError:
                pass
    
    def test_peer_info_model(self):
        """Тест модели PeerInfo"""
        peer = PeerInfo(
            peer_id="peer_123",
            address="192.168.1.1",
            port=8888
        )
        assert peer.peer_id == "peer_123"
        assert peer.address == "192.168.1.1"
        assert peer.port == 8888
        assert peer.reputation == 1.0
        assert peer.completed_tasks == 0
        assert peer.failed_tasks == 0
    
    @pytest.mark.asyncio
    async def test_distribute_task(self, node, temp_dir):
        """Тест распределения задачи"""
        # Создаем задачу
        task = Task(
            type=TaskType.SUM,
            data=[1, 2, 3, 4, 5],
            reward=10.0
        )
        
        # Мокаем libtorrent сессию
        mock_session = MagicMock()
        mock_handle = MagicMock()
        mock_session.add_torrent.return_value = mock_handle
        
        node.session = mock_session
        
        # Мокаем create_torrent
        with patch('torrentnode.node.create_torrent', return_value=b'fake_torrent_data'):
            # Мокаем lt.torrent_info
            with patch('torrentnode.node.lt.torrent_info') as mock_torrent_info:
                mock_info = MagicMock()
                mock_info.info_hash.return_value = b'fake_info_hash'
                mock_torrent_info.return_value = mock_info
                
                # Распределяем задачу
                torrent_hash = await node.distribute_task(task)
                
                assert torrent_hash is not None
                assert mock_session.add_torrent.called
                assert task.id in str(list((temp_dir / "data").glob("task_*"))[0])
    
    @pytest.mark.asyncio
    async def test_task_execution_flow(self, node):
        """Тест процесса выполнения задачи"""
        # Создаем mock торрент handle
        mock_handle = MagicMock()
        mock_info = MagicMock()
        mock_file = MagicMock()
        mock_file.path = "task.json"
        mock_info.files.return_value = [mock_file]
        mock_handle.torrent_file.return_value = mock_info
        mock_handle.save_path.return_value = str(node.config.data_dir)
        
        # Создаем файл с задачей
        task_data = {
            "id": "test_task_123",
            "type": "sum",
            "data": [1, 2, 3],
            "reward": 5.0
        }
        
        task_file = node.config.data_dir / "task.json"
        with open(task_file, 'w') as f:
            json.dump(task_data, f)
        
        # Выполняем задачу
        await node._extract_and_execute_task(mock_handle)
        
        # Проверяем статистику
        assert node.stats["tasks_completed"] == 1
        assert node.stats["tokens_earned"] == 5.0
    
    def test_balance_operations(self, node):
        """Тест операций с балансом"""
        # Инициализация баланса
        node.reward_system.init_balance(node.node_id)
        
        # Проверка начального баланса
        balance = node.get_balance()
        assert balance == 100.0  # INITIAL_BALANCE
        
        # Добавление вознаграждения
        node.reward_system.add_reward(node.node_id, 50.0, "test_task")
        balance = node.get_balance()
        assert balance == 150.0
    
    @pytest.mark.asyncio
    async def test_peer_management(self, node):
        """Тест управления пирами"""
        # Добавляем пиров
        peer1 = PeerInfo(
            peer_id="peer_001",
            address="192.168.1.1",
            port=8888
        )
        peer2 = PeerInfo(
            peer_id="peer_002",
            address="192.168.1.2",
            port=8889,
            last_seen=time.time() - 400  # Старый пир
        )
        
        node.peers[peer1.peer_id] = peer1
        node.peers[peer2.peer_id] = peer2
        
        assert len(node.peers) == 2
        
        # Запускаем обслуживание пиров
        node.running = True
        maintain_task = asyncio.create_task(node._maintain_peers())
        await asyncio.sleep(0.1)
        
        # Проверяем, что старый пир удален
        assert len(node.peers) == 1
        assert "peer_001" in node.peers
        assert "peer_002" not in node.peers
        
        # Останавливаем задачу
        node.running = False
        maintain_task.cancel()
        try:
            await maintain_task
        except asyncio.CancelledError:
            pass
    
    def test_task_signature(self, node):
        """Тест подписи и проверки задач"""
        task_data = {
            "id": "test_123",
            "type": "sum",
            "data": [1, 2, 3]
        }
        
        # Подписываем задачу
        signature = node._sign_task(task_data)
        assert isinstance(signature, str)
        assert len(signature) > 0
        
        # Проверяем подпись
        task_data["signature"] = signature
        is_valid = node._verify_task_signature(task_data.copy())
        assert is_valid is True
        
        # Проверяем неверную подпись
        task_data["signature"] = "invalid_signature"
        is_valid = node._verify_task_signature(task_data.copy())
        assert is_valid is False
    
    def test_save_state(self, node):
        """Тест сохранения состояния ноды"""
        # Добавляем некоторые данные
        node.stats["tasks_completed"] = 10
        node.stats["tokens_earned"] = 100.0
        
        peer = PeerInfo(
            peer_id="test_peer",
            address="192.168.1.1",
            port=8888
        )
        node.peers[peer.peer_id] = peer
        
        # Сохраняем состояние
        node._save_state()
        
        # Проверяем файл
        state_file = node.config.data_dir / "node_state.json"
        assert state_file.exists()
        
        # Загружаем и проверяем данные
        with open(state_file) as f:
            state = json.load(f)
        
        assert state["node_id"] == node.node_id
        assert state["stats"]["tasks_completed"] == 10
        assert state["stats"]["tokens_earned"] == 100.0
        assert len(state["peers"]) == 1
        assert state["peers"][0]["peer_id"] == "test_peer"


class TestIntegration:
    """Интеграционные тесты"""
    
    @pytest.mark.asyncio
    async def test_two_nodes_communication(self, temp_dir):
        """Тест взаимодействия двух нод"""
        # Создаем две ноды
        config1 = NodeConfig(
            name="node1",
            port=28888,
            data_dir=temp_dir / "node1",
            enable_dht=False
        )
        config2 = NodeConfig(
            name="node2",
            port=28889,
            data_dir=temp_dir / "node2",
            enable_dht=False,
            bootstrap_nodes=["localhost:28888"]
        )
        
        node1 = Node(config1)
        node2 = Node(config2)
        
        # Мокаем libtorrent сессии
        with patch.object(node1, '_create_session', return_value=MagicMock()):
            with patch.object(node2, '_create_session', return_value=MagicMock()):
                # Запускаем ноды
                task1 = asyncio.create_task(node1.start())
                task2 = asyncio.create_task(node2.start())
                
                await asyncio.sleep(0.1)
                
                assert node1.running is True
                assert node2.running is True
                
                # Останавливаем ноды
                await node1.stop()
                await node2.stop()
                
                # Отменяем задачи
                for task in [task1, task2]:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
    
    @pytest.mark.asyncio
    async def test_full_task_lifecycle(self, temp_dir):
        """Тест полного жизненного цикла задачи"""
        # Создаем ноду
        config = NodeConfig(
            data_dir=temp_dir / "test_node",
            enable_dht=False
        )
        node = Node(config)
        
        # Создаем задачу
        task = Task(
            id="lifecycle_test",
            type=TaskType.SUM,
            data=[10, 20, 30, 40],
            reward=15.0
        )
        
        # Мокаем необходимые компоненты
        with patch.object(node, '_create_session', return_value=MagicMock()):
            node.session = MagicMock()
            
            # Тест 1: Распределение задачи
            with patch('torrentnode.node.create_torrent', return_value=b'torrent_data'):
                with patch('torrentnode.node.lt.torrent_info') as mock_info:
                    mock_info.return_value = MagicMock(
                        info_hash=MagicMock(return_value=b'test_hash')
                    )
                    
                    torrent_hash = await node.distribute_task(task)
                    assert torrent_hash is not None
            
            # Тест 2: Выполнение задачи
            result = await node.task_executor.execute(task)
            assert result.success is True
            assert result.result == 100  # sum([10, 20, 30, 40])
            
            # Тест 3: Начисление вознаграждения
            node.reward_system.init_balance(node.node_id)
            initial_balance = node.get_balance()
            
            node.reward_system.add_reward(node.node_id, task.reward, task.id)
            final_balance = node.get_balance()
            
            assert final_balance == initial_balance + task.reward 