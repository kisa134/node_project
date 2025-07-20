"""
Модуль системы вознаграждений

Управляет токенами, балансами и интеграцией с блокчейном.
"""

import json
import os
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import structlog
from pydantic import BaseModel, Field
from web3 import Web3
from web3.contract import Contract
from web3.exceptions import ContractLogicError

logger = structlog.get_logger()


@dataclass
class TokenBalance:
    """Баланс токенов"""
    address: str
    balance: float
    locked: float = 0.0
    earned_total: float = 0.0
    spent_total: float = 0.0
    last_updated: float = Field(default_factory=time.time)


class Transaction(BaseModel):
    """Модель транзакции"""
    id: int = None
    from_address: str
    to_address: str
    amount: float
    tx_type: str  # 'reward', 'transfer', 'stake', 'unstake'
    task_id: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)
    block_number: Optional[int] = None
    tx_hash: Optional[str] = None


class RewardSystem:
    """Система вознаграждений TorrentNode"""
    
    INITIAL_BALANCE = 100.0
    DECIMALS = 18
    
    # ABI упрощенного ERC-20 контракта
    ERC20_ABI = json.loads('''[
        {
            "constant": true,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}],
            "name": "mint",
            "outputs": [],
            "type": "function"
        }
    ]''')
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
        # Web3 интеграция (опциональна)
        self.w3: Optional[Web3] = None
        self.contract: Optional[Contract] = None
        self.account: Optional[str] = None
        
        # Попытка подключения к Web3
        self._init_web3()
    
    def _init_db(self):
        """Инициализация локальной базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS balances (
                    address TEXT PRIMARY KEY,
                    balance REAL DEFAULT 0.0,
                    locked REAL DEFAULT 0.0,
                    earned_total REAL DEFAULT 0.0,
                    spent_total REAL DEFAULT 0.0,
                    last_updated REAL,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_address TEXT NOT NULL,
                    to_address TEXT NOT NULL,
                    amount REAL NOT NULL,
                    tx_type TEXT NOT NULL,
                    task_id TEXT,
                    timestamp REAL NOT NULL,
                    block_number INTEGER,
                    tx_hash TEXT,
                    FOREIGN KEY (from_address) REFERENCES balances(address),
                    FOREIGN KEY (to_address) REFERENCES balances(address)
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_tx_from ON transactions(from_address);
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_tx_to ON transactions(to_address);
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_tx_timestamp ON transactions(timestamp);
            ''')
            
            conn.commit()
        
        logger.info("Reward database initialized", db_path=str(self.db_path))
    
    def _init_web3(self):
        """Инициализация Web3 подключения"""
        try:
            # Проверка переменных окружения
            eth_network = os.getenv('ETH_NETWORK', '')
            eth_private_key = os.getenv('ETH_PRIVATE_KEY', '')
            contract_address = os.getenv('ETH_CONTRACT_ADDRESS', '')
            web3_enabled = os.getenv('WEB3_ENABLED', 'false').lower() == 'true'
            
            if not web3_enabled:
                logger.info("Web3 integration disabled")
                return
            
            if not all([eth_network, eth_private_key, contract_address]):
                logger.warning("Web3 credentials not fully configured")
                return
            
            # Подключение к сети
            if eth_network == 'sepolia':
                rpc_url = 'https://sepolia.infura.io/v3/YOUR_INFURA_KEY'
            elif eth_network == 'localhost':
                rpc_url = 'http://localhost:8545'
            else:
                rpc_url = eth_network
            
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            if not self.w3.is_connected():
                logger.error("Failed to connect to Ethereum network")
                self.w3 = None
                return
            
            # Настройка аккаунта
            self.account = self.w3.eth.account.from_key(eth_private_key)
            
            # Инициализация контракта
            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=self.ERC20_ABI
            )
            
            logger.info(
                "Web3 initialized",
                network=eth_network,
                account=self.account.address,
                contract=contract_address
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize Web3: {e}")
            self.w3 = None
            self.contract = None
    
    def init_balance(self, address: str) -> TokenBalance:
        """Инициализация баланса для нового адреса"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Проверка существования
            cursor.execute(
                "SELECT balance FROM balances WHERE address = ?",
                (address,)
            )
            
            if cursor.fetchone() is None:
                # Создание нового баланса
                cursor.execute(
                    """INSERT INTO balances 
                    (address, balance, locked, earned_total, spent_total, last_updated) 
                    VALUES (?, ?, 0, 0, 0, ?)""",
                    (address, self.INITIAL_BALANCE, time.time())
                )
                
                # Запись транзакции начисления
                cursor.execute(
                    """INSERT INTO transactions 
                    (from_address, to_address, amount, tx_type, timestamp) 
                    VALUES (?, ?, ?, ?, ?)""",
                    ('system', address, self.INITIAL_BALANCE, 'initial', time.time())
                )
                
                conn.commit()
                logger.info(f"Initialized balance for {address}: {self.INITIAL_BALANCE}")
            
            return self.get_balance_info(address)
    
    def get_balance(self, address: str) -> float:
        """Получение баланса адреса"""
        # Сначала проверяем блокчейн если доступен
        if self.w3 and self.contract:
            try:
                balance_wei = self.contract.functions.balanceOf(
                    Web3.to_checksum_address(address)
                ).call()
                balance = Web3.from_wei(balance_wei, 'ether')
                
                # Синхронизация с локальной БД
                self._sync_balance(address, balance)
                return float(balance)
            except Exception as e:
                logger.warning(f"Failed to get blockchain balance: {e}")
        
        # Возврат локального баланса
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT balance FROM balances WHERE address = ?",
                (address,)
            )
            result = cursor.fetchone()
            return result[0] if result else 0.0
    
    def get_balance_info(self, address: str) -> TokenBalance:
        """Получение полной информации о балансе"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT address, balance, locked, earned_total, 
                spent_total, last_updated FROM balances WHERE address = ?""",
                (address,)
            )
            result = cursor.fetchone()
            
            if result:
                return TokenBalance(
                    address=result[0],
                    balance=result[1],
                    locked=result[2],
                    earned_total=result[3],
                    spent_total=result[4],
                    last_updated=result[5]
                )
            else:
                return TokenBalance(address=address, balance=0.0)
    
    def add_reward(self, address: str, amount: float, task_id: Optional[str] = None) -> bool:
        """Начисление вознаграждения за выполнение задачи"""
        if amount <= 0:
            logger.error("Invalid reward amount", amount=amount)
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                # Обновление баланса
                cursor.execute(
                    """UPDATE balances 
                    SET balance = balance + ?, 
                        earned_total = earned_total + ?,
                        last_updated = ?
                    WHERE address = ?""",
                    (amount, amount, time.time(), address)
                )
                
                # Запись транзакции
                cursor.execute(
                    """INSERT INTO transactions 
                    (from_address, to_address, amount, tx_type, task_id, timestamp) 
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    ('rewards_pool', address, amount, 'reward', task_id, time.time())
                )
                
                conn.commit()
                
                # Попытка записи в блокчейн
                if self.w3 and self.contract:
                    self._mint_tokens(address, amount)
                
                logger.info(f"Reward added: {address} +{amount} tokens")
                return True
                
            except Exception as e:
                logger.error(f"Failed to add reward: {e}")
                conn.rollback()
                return False
    
    def transfer(self, from_address: str, to_address: str, amount: float) -> Tuple[bool, str]:
        """Перевод токенов между адресами"""
        if amount <= 0:
            return False, "Invalid amount"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                # Проверка баланса
                balance = self.get_balance(from_address)
                if balance < amount:
                    return False, "Insufficient balance"
                
                # Обновление балансов
                cursor.execute(
                    """UPDATE balances 
                    SET balance = balance - ?, 
                        spent_total = spent_total + ?,
                        last_updated = ?
                    WHERE address = ?""",
                    (amount, amount, time.time(), from_address)
                )
                
                cursor.execute(
                    """UPDATE balances 
                    SET balance = balance + ?, 
                        last_updated = ?
                    WHERE address = ?""",
                    (amount, time.time(), to_address)
                )
                
                # Запись транзакции
                cursor.execute(
                    """INSERT INTO transactions 
                    (from_address, to_address, amount, tx_type, timestamp) 
                    VALUES (?, ?, ?, ?, ?)""",
                    (from_address, to_address, amount, 'transfer', time.time())
                )
                
                conn.commit()
                
                # Попытка записи в блокчейн
                tx_hash = None
                if self.w3 and self.contract:
                    tx_hash = self._transfer_on_chain(from_address, to_address, amount)
                
                logger.info(f"Transfer: {from_address} -> {to_address}: {amount}")
                return True, tx_hash or "Success"
                
            except Exception as e:
                logger.error(f"Transfer failed: {e}")
                conn.rollback()
                return False, str(e)
    
    def get_transactions(self, address: str, limit: int = 100) -> List[Transaction]:
        """Получение истории транзакций"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, from_address, to_address, amount, tx_type, 
                task_id, timestamp, block_number, tx_hash
                FROM transactions 
                WHERE from_address = ? OR to_address = ?
                ORDER BY timestamp DESC
                LIMIT ?""",
                (address, address, limit)
            )
            
            transactions = []
            for row in cursor.fetchall():
                transactions.append(Transaction(
                    id=row[0],
                    from_address=row[1],
                    to_address=row[2],
                    amount=row[3],
                    tx_type=row[4],
                    task_id=row[5],
                    timestamp=row[6],
                    block_number=row[7],
                    tx_hash=row[8]
                ))
            
            return transactions
    
    def get_leaderboard(self, limit: int = 10) -> List[Tuple[str, float, float]]:
        """Получение таблицы лидеров"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT address, balance, earned_total 
                FROM balances 
                ORDER BY earned_total DESC 
                LIMIT ?""",
                (limit,)
            )
            
            return [(row[0], row[1], row[2]) for row in cursor.fetchall()]
    
    def stake(self, address: str, amount: float) -> bool:
        """Стейкинг токенов"""
        if amount <= 0:
            return False
        
        balance = self.get_balance(address)
        if balance < amount:
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                # Перевод из баланса в заблокированные
                cursor.execute(
                    """UPDATE balances 
                    SET balance = balance - ?, 
                        locked = locked + ?,
                        last_updated = ?
                    WHERE address = ?""",
                    (amount, amount, time.time(), address)
                )
                
                # Запись транзакции
                cursor.execute(
                    """INSERT INTO transactions 
                    (from_address, to_address, amount, tx_type, timestamp) 
                    VALUES (?, ?, ?, ?, ?)""",
                    (address, 'staking_pool', amount, 'stake', time.time())
                )
                
                conn.commit()
                logger.info(f"Staked: {address} locked {amount} tokens")
                return True
                
            except Exception as e:
                logger.error(f"Staking failed: {e}")
                conn.rollback()
                return False
    
    def unstake(self, address: str, amount: float) -> bool:
        """Разблокировка токенов"""
        if amount <= 0:
            return False
        
        balance_info = self.get_balance_info(address)
        if balance_info.locked < amount:
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                # Перевод из заблокированных в баланс
                cursor.execute(
                    """UPDATE balances 
                    SET balance = balance + ?, 
                        locked = locked - ?,
                        last_updated = ?
                    WHERE address = ?""",
                    (amount, amount, time.time(), address)
                )
                
                # Запись транзакции
                cursor.execute(
                    """INSERT INTO transactions 
                    (from_address, to_address, amount, tx_type, timestamp) 
                    VALUES (?, ?, ?, ?, ?)""",
                    ('staking_pool', address, amount, 'unstake', time.time())
                )
                
                conn.commit()
                logger.info(f"Unstaked: {address} unlocked {amount} tokens")
                return True
                
            except Exception as e:
                logger.error(f"Unstaking failed: {e}")
                conn.rollback()
                return False
    
    def _sync_balance(self, address: str, blockchain_balance: float):
        """Синхронизация баланса с блокчейном"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE balances 
                SET balance = ?, last_updated = ?
                WHERE address = ?""",
                (blockchain_balance, time.time(), address)
            )
            conn.commit()
    
    def _mint_tokens(self, address: str, amount: float):
        """Минтинг токенов в блокчейне"""
        if not self.w3 or not self.contract or not self.account:
            return
        
        try:
            # Подготовка транзакции
            amount_wei = Web3.to_wei(amount, 'ether')
            
            tx = self.contract.functions.mint(
                Web3.to_checksum_address(address),
                amount_wei
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
            })
            
            # Подпись и отправка
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            logger.info(f"Minted tokens on chain: {tx_hash.hex()}")
            
        except Exception as e:
            logger.error(f"Failed to mint tokens on chain: {e}")
    
    def _transfer_on_chain(self, from_address: str, to_address: str, amount: float) -> Optional[str]:
        """Перевод токенов в блокчейне"""
        if not self.w3 or not self.contract:
            return None
        
        try:
            # Здесь должна быть логика подписи транзакции от имени from_address
            # Для упрощения пропускаем
            logger.warning("On-chain transfer not implemented for user addresses")
            return None
            
        except Exception as e:
            logger.error(f"Failed to transfer on chain: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение общей статистики системы"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Общее количество адресов
            cursor.execute("SELECT COUNT(*) FROM balances")
            total_addresses = cursor.fetchone()[0]
            
            # Общий объем токенов
            cursor.execute("SELECT SUM(balance), SUM(locked) FROM balances")
            total_supply, total_locked = cursor.fetchone()
            
            # Количество транзакций
            cursor.execute("SELECT COUNT(*) FROM transactions")
            total_transactions = cursor.fetchone()[0]
            
            # Объем вознаграждений
            cursor.execute(
                "SELECT SUM(amount) FROM transactions WHERE tx_type = 'reward'"
            )
            total_rewards = cursor.fetchone()[0] or 0
            
            return {
                'total_addresses': total_addresses,
                'total_supply': total_supply or 0,
                'total_locked': total_locked or 0,
                'total_transactions': total_transactions,
                'total_rewards_distributed': total_rewards,
                'initial_balance_per_node': self.INITIAL_BALANCE,
                'blockchain_connected': self.w3 is not None
            }


# Пример использования
if __name__ == "__main__":
    # Создание системы вознаграждений
    rewards = RewardSystem("./test_tokens.db")
    
    # Инициализация нескольких адресов
    node1 = "node_001"
    node2 = "node_002"
    node3 = "node_003"
    
    rewards.init_balance(node1)
    rewards.init_balance(node2)
    rewards.init_balance(node3)
    
    # Начисление вознаграждений
    rewards.add_reward(node1, 50.0, "task_123")
    rewards.add_reward(node2, 30.0, "task_124")
    
    # Перевод токенов
    success, msg = rewards.transfer(node1, node3, 25.0)
    print(f"Transfer result: {success}, {msg}")
    
    # Стейкинг
    rewards.stake(node2, 50.0)
    
    # Вывод балансов
    for node in [node1, node2, node3]:
        balance_info = rewards.get_balance_info(node)
        print(f"\n{node}:")
        print(f"  Balance: {balance_info.balance}")
        print(f"  Locked: {balance_info.locked}")
        print(f"  Earned: {balance_info.earned_total}")
    
    # Таблица лидеров
    print("\nLeaderboard:")
    for address, balance, earned in rewards.get_leaderboard():
        print(f"  {address}: {balance} tokens (earned: {earned})")
    
    # Статистика
    print("\nSystem Statistics:")
    stats = rewards.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}") 