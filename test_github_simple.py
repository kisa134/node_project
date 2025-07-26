#!/usr/bin/env python3
"""
Упрощенное тестирование GitHub интеграции SwarmMind
"""

import os
import sys
from github_integration import GitHubIntegration
from swarm_mind.logger import log_event

def test_github_connection():
    """Тестирование подключения к GitHub"""
    print("🔗 Тестирование подключения к GitHub...")
    
    # Настройки из переменных окружения
    token = os.getenv('GITHUB_TOKEN')
    repo_owner = os.getenv('GITHUB_REPO_OWNER', 'kisa134')
    repo_name = os.getenv('GITHUB_REPO_NAME', 'node_project')
    
    if not token:
        print("❌ GITHUB_TOKEN не найден в переменных окружения")
        return None
    
    github = GitHubIntegration(token, repo_owner, repo_name)
    
    if github.test_connection():
        print("✅ Подключение к GitHub успешно!")
        return github
    else:
        print("❌ Ошибка подключения к GitHub")
        return None

def test_repository_analysis(github):
    """Тестирование анализа репозитория"""
    print("\n📊 Анализ репозитория...")
    
    # Получаем список файлов
    files = github.get_repository_files()
    print(f"📁 Найдено файлов в репозитории: {len(files)}")
    
    # Анализируем несколько файлов
    python_files = [f for f in files if f['name'].endswith('.py')]
    print(f"🐍 Python файлов: {len(python_files)}")
    
    for file_info in python_files[:3]:  # Анализируем первые 3 файла
        file_path = file_info['path']
        content = github.get_file_content(file_path)
        if content:
            improvements = github.analyze_code_quality(file_path, content)
            if improvements:
                print(f"💡 Найдено улучшений в {file_path}: {len(improvements)}")
                for imp in improvements[:2]:  # Показываем первые 2 улучшения
                    print(f"   - {imp.description}")
    
    return True

def main():
    """Главная функция тестирования"""
    print("🌌============================================================🌌")
    print("🚀           SWARMIND GITHUB INTEGRATION TEST           🚀")
    print("🧬         AUTONOMOUS CODE IMPROVEMENT DEMO             🧬")
    print("⚡         TECHNOLOGICAL SINGULARITY PROTOCOL          ⚡")
    print("🌌============================================================🌌")
    
    # Тестируем подключение
    github = test_github_connection()
    if not github:
        return
    
    # Тестируем анализ репозитория
    if not test_repository_analysis(github):
        return
    
    print("\n🎉 GitHub интеграция работает успешно!")
    print("🚀 SwarmMind готов к автономному саморазвитию!")
    print("\n📋 Что теперь можно делать:")
    print("   - Запустить unified_interface.py для полного интерфейса")
    print("   - Использовать вкладку GitHub для ручного управления")
    print("   - Настроить автоматические улучшения по расписанию")

if __name__ == "__main__":
    main() 