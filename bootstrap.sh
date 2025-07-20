#!/bin/bash

# TorrentNode Net Bootstrap Script
# Автоматическая установка и запуск проекта

set -e

echo "🚀 TorrentNode Net Bootstrap"
echo "==========================="

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Функция для вывода статуса
status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Проверка Python версии
check_python() {
    echo "Проверка Python..."
    if command -v python3.11 &> /dev/null; then
        PYTHON_CMD=python3.11
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD=python3
    elif command -v python &> /dev/null; then
        PYTHON_CMD=python
    else
        error "Python не найден. Установите Python 3.11+"
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    status "Python версия: $PYTHON_VERSION"
    
    # Проверка минимальной версии
    REQUIRED_VERSION="3.11"
    if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
        error "Требуется Python 3.11 или выше"
    fi
}

# Проверка и установка Poetry
check_poetry() {
    echo "Проверка Poetry..."
    if ! command -v poetry &> /dev/null; then
        warning "Poetry не найден. Устанавливаю..."
        curl -sSL https://install.python-poetry.org | $PYTHON_CMD -
        export PATH="$HOME/.local/bin:$PATH"
        
        if ! command -v poetry &> /dev/null; then
            error "Не удалось установить Poetry"
        fi
    fi
    status "Poetry установлен"
}

# Установка зависимостей
install_dependencies() {
    echo "Установка зависимостей..."
    
    if [ -f "pyproject.toml" ]; then
        poetry install
        status "Зависимости установлены через Poetry"
    elif [ -f "requirements.txt" ]; then
        $PYTHON_CMD -m pip install -r requirements.txt
        status "Зависимости установлены через pip"
    else
        # Создаем минимальный requirements.txt если нет файлов зависимостей
        warning "Файлы зависимостей не найдены. Создаю requirements.txt..."
        cat > requirements.txt << EOF
python-libtorrent>=2.0.0
cryptography>=41.0.0
web3>=6.0.0
aiofiles>=23.0.0
aiohttp>=3.9.0
pydantic>=2.0.0
click>=8.1.0
rich>=13.0.0
structlog>=24.0.0
python-dotenv>=1.0.0
psutil>=5.9.0
numpy>=1.24.0
requests>=2.31.0
bencodepy>=0.9.5
kademlia>=2.2.2
fastapi>=0.100.0
uvicorn>=0.23.0
EOF
        $PYTHON_CMD -m pip install -r requirements.txt
        status "Базовые зависимости установлены"
    fi
}

# Создание директорий
setup_directories() {
    echo "Создание директорий..."
    mkdir -p torrentnode
    mkdir -p tests
    mkdir -p infra
    mkdir -p .github/workflows
    mkdir -p logs
    mkdir -p data
    mkdir -p torrents
    status "Директории созданы"
}

# Проверка Docker (опционально)
check_docker() {
    echo "Проверка Docker..."
    if command -v docker &> /dev/null; then
        status "Docker установлен"
        
        if command -v docker-compose &> /dev/null; then
            status "Docker Compose установлен"
        else
            warning "Docker Compose не найден"
        fi
    else
        warning "Docker не установлен (опционально)"
    fi
}

# Генерация .env файла
generate_env() {
    if [ ! -f ".env" ]; then
        echo "Создание .env файла..."
        cat > .env << EOF
# TorrentNode Net Configuration
NODE_NAME=node_$(date +%s)
NODE_PORT=8888
LOG_LEVEL=INFO
DATA_DIR=./data
TORRENT_DIR=./torrents
TOKEN_DB=./tokens.db

# Network settings
DHT_ENABLED=true
BOOTSTRAP_NODES=
MAX_PEERS=50
UPLOAD_RATE_LIMIT=0
DOWNLOAD_RATE_LIMIT=0

# Security
ENABLE_ENCRYPTION=true
SECRET_KEY=$(openssl rand -hex 32)

# Task execution
MAX_CONCURRENT_TASKS=5
TASK_TIMEOUT=300
SANDBOX_ENABLED=true

# Rewards
INITIAL_BALANCE=100
TASK_REWARD=10

# Web3 (optional)
WEB3_ENABLED=false
ETH_NETWORK=sepolia
ETH_PRIVATE_KEY=
ETH_CONTRACT_ADDRESS=
EOF
        status ".env файл создан"
    else
        status ".env файл уже существует"
    fi
}

# Запуск ноды
run_node() {
    echo ""
    echo "🎉 Установка завершена!"
    echo ""
    echo "Доступные команды:"
    echo "  1. Запустить одну ноду"
    echo "  2. Запустить несколько нод"
    echo "  3. Запустить через Docker"
    echo "  4. Запустить тесты"
    echo "  5. Выход"
    echo ""
    
    read -p "Выберите действие (1-5): " choice
    
    case $choice in
        1)
            echo "Запуск ноды..."
            if [ -f "pyproject.toml" ]; then
                poetry run python -m torrentnode.node
            else
                $PYTHON_CMD -m torrentnode.node
            fi
            ;;
        2)
            echo "Запуск первой ноды на порту 8888..."
            if [ -f "pyproject.toml" ]; then
                poetry run python -m torrentnode.node --port 8888 --name node1 &
                NODE1_PID=$!
                sleep 3
                echo "Запуск второй ноды на порту 8889..."
                poetry run python -m torrentnode.node --port 8889 --name node2 --bootstrap localhost:8888 &
                NODE2_PID=$!
                echo ""
                echo "Ноды запущены! PID: $NODE1_PID, $NODE2_PID"
                echo "Нажмите Ctrl+C для остановки"
                wait
            else
                $PYTHON_CMD -m torrentnode.node --port 8888 --name node1 &
                NODE1_PID=$!
                sleep 3
                $PYTHON_CMD -m torrentnode.node --port 8889 --name node2 --bootstrap localhost:8888 &
                NODE2_PID=$!
                echo ""
                echo "Ноды запущены! PID: $NODE1_PID, $NODE2_PID"
                echo "Нажмите Ctrl+C для остановки"
                wait
            fi
            ;;
        3)
            if command -v docker-compose &> /dev/null; then
                echo "Запуск через Docker..."
                docker-compose -f infra/docker-compose.yml up
            else
                error "Docker Compose не установлен"
            fi
            ;;
        4)
            echo "Запуск тестов..."
            if [ -f "pyproject.toml" ]; then
                poetry run pytest
            else
                $PYTHON_CMD -m pytest
            fi
            ;;
        5)
            echo "Выход"
            exit 0
            ;;
        *)
            error "Неверный выбор"
            ;;
    esac
}

# Основной процесс
main() {
    echo ""
    check_python
    check_poetry
    setup_directories
    install_dependencies
    check_docker
    generate_env
    echo ""
    run_node
}

# Обработка прерывания
trap 'echo ""; echo "Остановка..."; kill $(jobs -p) 2>/dev/null; exit' INT

# Запуск
main 