#!/usr/bin/env python3
"""
🔗 GITHUB INTEGRATION FOR SWARMIND 🔗

Модуль для интеграции с GitHub API:
- Анализ кода репозитория
- Автоматические предложения улучшений
- Создание pull requests
- Self-improvement через реальные обновления кода
"""

import os
import json
import requests
import base64
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from swarm_mind.logger import log_event

@dataclass
class CodeImprovement:
    file_path: str
    current_code: str
    suggested_code: str
    improvement_type: str  # 'performance', 'security', 'readability', 'bugfix'
    description: str
    priority: int  # 1-5, где 5 - критично

@dataclass
class PullRequest:
    title: str
    description: str
    branch_name: str
    improvements: List[CodeImprovement]

class GitHubIntegration:
    def __init__(self, token: str, repo_owner: str, repo_name: str):
        self.token = token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
    def test_connection(self) -> bool:
        """Проверка подключения к GitHub API"""
        try:
            response = requests.get(self.base_url, headers=self.headers)
            if response.status_code == 200:
                log_event("GitHub API connection successful")
                return True
            else:
                log_event(f"GitHub API connection failed: {response.status_code}")
                return False
        except Exception as e:
            log_event(f"GitHub API connection error: {str(e)}")
            return False
    
    def get_repository_files(self, path: str = "") -> List[Dict]:
        """Получение списка файлов в репозитории"""
        try:
            url = f"{self.base_url}/contents/{path}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                log_event(f"Failed to get repository files: {response.status_code}")
                return []
        except Exception as e:
            log_event(f"Error getting repository files: {str(e)}")
            return []
    
    def get_file_content(self, file_path: str) -> Optional[str]:
        """Получение содержимого файла"""
        try:
            url = f"{self.base_url}/contents/{file_path}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                content = response.json()["content"]
                return base64.b64decode(content).decode('utf-8')
            else:
                log_event(f"Failed to get file content: {response.status_code}")
                return None
        except Exception as e:
            log_event(f"Error getting file content: {str(e)}")
            return None
    
    def analyze_code_quality(self, file_path: str, content: str) -> List[CodeImprovement]:
        """Анализ качества кода и предложение улучшений"""
        improvements = []
        
        # Простые правила анализа (можно расширить с помощью AI)
        lines = content.split('\n')
        
        # Проверка на длинные функции
        function_lines = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('def ') or line.strip().startswith('async def '):
                function_lines = 0
            elif line.strip():
                function_lines += 1
                if function_lines > 50:
                    improvements.append(CodeImprovement(
                        file_path=file_path,
                        current_code="",
                        suggested_code="",
                        improvement_type="readability",
                        description=f"Функция слишком длинная (более 50 строк) на строке {i+1}",
                        priority=3
                    ))
                    break
        
        # Проверка на комментарии
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        if len(lines) > 20 and comment_lines < len(lines) * 0.1:
            improvements.append(CodeImprovement(
                file_path=file_path,
                current_code="",
                suggested_code="",
                improvement_type="readability",
                description="Недостаточно комментариев в коде",
                priority=2
            ))
        
        # Проверка на обработку исключений
        if 'import' in content and 'try:' not in content and 'except' not in content:
            improvements.append(CodeImprovement(
                file_path=file_path,
                current_code="",
                suggested_code="",
                improvement_type="security",
                description="Отсутствует обработка исключений",
                priority=4
            ))
        
        return improvements
    
    def create_branch(self, branch_name: str) -> bool:
        """Создание новой ветки"""
        try:
            # Получаем SHA последнего коммита
            response = requests.get(f"{self.base_url}/git/refs/heads/main", headers=self.headers)
            if response.status_code != 200:
                response = requests.get(f"{self.base_url}/git/refs/heads/master", headers=self.headers)
            
            if response.status_code == 200:
                sha = response.json()["object"]["sha"]
                
                # Создаем новую ветку
                data = {
                    "ref": f"refs/heads/{branch_name}",
                    "sha": sha
                }
                response = requests.post(f"{self.base_url}/git/refs", headers=self.headers, json=data)
                
                if response.status_code == 201:
                    log_event(f"Created branch: {branch_name}")
                    return True
                else:
                    log_event(f"Failed to create branch: {response.status_code}")
                    return False
            else:
                log_event("Failed to get base branch SHA")
                return False
        except Exception as e:
            log_event(f"Error creating branch: {str(e)}")
            return False
    
    def update_file(self, file_path: str, content: str, message: str, branch: str) -> bool:
        """Обновление файла в репозитории"""
        try:
            # Получаем текущий SHA файла
            response = requests.get(f"{self.base_url}/contents/{file_path}?ref={branch}", headers=self.headers)
            if response.status_code == 200:
                sha = response.json()["sha"]
            else:
                sha = None
            
            # Обновляем файл
            data = {
                "message": message,
                "content": base64.b64encode(content.encode()).decode(),
                "branch": branch
            }
            if sha:
                data["sha"] = sha
            
            response = requests.put(f"{self.base_url}/contents/{file_path}", headers=self.headers, json=data)
            
            if response.status_code in [200, 201]:
                log_event(f"Updated file: {file_path}")
                return True
            else:
                log_event(f"Failed to update file: {response.status_code}")
                return False
        except Exception as e:
            log_event(f"Error updating file: {str(e)}")
            return False
    
    def create_pull_request(self, pr: PullRequest) -> bool:
        """Создание pull request"""
        try:
            data = {
                "title": pr.title,
                "body": pr.description,
                "head": pr.branch_name,
                "base": "main"
            }
            
            response = requests.post(f"{self.base_url}/pulls", headers=self.headers, json=data)
            
            if response.status_code == 201:
                pr_url = response.json()["html_url"]
                log_event(f"Created pull request: {pr_url}")
                return True
            else:
                log_event(f"Failed to create pull request: {response.status_code}")
                return False
        except Exception as e:
            log_event(f"Error creating pull request: {str(e)}")
            return False
    
    def auto_improve_repository(self) -> List[PullRequest]:
        """Автоматическое улучшение репозитория"""
        improvements_found = []
        
        # Получаем все файлы Python
        files = self.get_repository_files()
        python_files = []
        
        for file in files:
            if file["name"].endswith('.py'):
                python_files.append(file["path"])
        
        # Анализируем каждый файл
        for file_path in python_files:
            content = self.get_file_content(file_path)
            if content:
                file_improvements = self.analyze_code_quality(file_path, content)
                if file_improvements:
                    improvements_found.extend(file_improvements)
        
        # Группируем улучшения по типам
        if improvements_found:
            pr = PullRequest(
                title=f"Auto-improvement: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                description="Автоматические улучшения кода от SwarmMind AI",
                branch_name=f"swarmmind-improvements-{datetime.now().strftime('%Y%m%d-%H%M')}",
                improvements=improvements_found
            )
            
            # Создаем ветку и pull request
            if self.create_branch(pr.branch_name):
                # Здесь можно добавить реальные изменения файлов
                return [pr]
        
        return []

# Пример использования
def setup_github_integration():
    """Настройка GitHub интеграции"""
    # Загружаем переменные из .env файла
    from dotenv import load_dotenv
    load_dotenv()
    
    token = os.getenv('GITHUB_TOKEN')
    repo_owner = os.getenv('GITHUB_REPO_OWNER', 'kisa134')
    repo_name = os.getenv('GITHUB_REPO_NAME', 'node_project')
    
    if not token:
        log_event("GitHub token not found. Set GITHUB_TOKEN environment variable.")
        return None
    
    github = GitHubIntegration(token, repo_owner, repo_name)
    
    if github.test_connection():
        log_event("GitHub integration setup successful")
        return github
    else:
        log_event("GitHub integration setup failed")
        return None 