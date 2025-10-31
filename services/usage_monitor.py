"""
Token用量监控模块 - 跟踪每日API使用量和token消耗
"""
import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Optional
from threading import Lock


class UsageMonitor:
    """API用量监控器"""
    
    def __init__(self, storage_file: str = "usage_data.json"):
        self.storage_file = Path(storage_file)
        self.lock = Lock()
        
        # Gemini模型每日请求限制（免费层级）
        # 注意：使用标准化模型名称（用于配额跟踪）
        self.model_limits = {
            "gemini-2.5-pro": {
                "rpd": 50,  # Requests Per Day
                "tpm": 125000,  # Tokens Per Minute
            },
            "gemini-2.5-flash": {
                "rpd": 250,
                "tpm": 250000,
            },
            "gemini-2.0-flash": {
                "rpd": 200,
                "tpm": 1000000,
            }
        }
        
        # 加载历史数据
        self.usage_data = self._load_usage_data()
    
    def _load_usage_data(self) -> Dict:
        """加载用量数据"""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 清理过期数据（只保留最近的数据）
                    today = date.today().isoformat()
                    return {k: v for k, v in data.items() if k >= today or k == "current_date"}
            except Exception as e:
                print(f"加载用量数据失败: {e}")
        
        return {}
    
    def _save_usage_data(self):
        """保存用量数据"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存用量数据失败: {e}")
    
    def _get_today_key(self) -> str:
        """获取今天的日期键"""
        return date.today().isoformat()
    
    def _get_model_usage(self, model: str) -> Dict:
        """获取指定模型的今日用量"""
        today = self._get_today_key()
        model_key = f"{today}_{model}"
        
        if model_key not in self.usage_data:
            self.usage_data[model_key] = {
                "requests": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0
            }
        
        return self.usage_data[model_key]
    
    def check_quota(self, model: str) -> Dict:
        """
        检查是否还有配额
        
        Args:
            model: 模型名称
            
        Returns:
            包含是否可用、剩余配额等信息的字典
        """
        with self.lock:
            if model not in self.model_limits:
                return {
                    "available": False,
                    "reason": f"未知模型: {model}"
                }
            
            usage = self._get_model_usage(model)
            limit = self.model_limits[model]
            
            remaining_requests = limit["rpd"] - usage["requests"]
            
            return {
                "available": remaining_requests > 0,
                "remaining_requests": max(0, remaining_requests),
                "used_requests": usage["requests"],
                "total_requests": limit["rpd"],
                "used_tokens": usage["total_tokens"],
                "tpm_limit": limit["tpm"],
                "model": model
            }
    
    def record_usage(self, model: str, input_tokens: int, output_tokens: int):
        """
        记录API使用量
        
        Args:
            model: 模型名称
            input_tokens: 输入token数量
            output_tokens: 输出token数量
        """
        with self.lock:
            usage = self._get_model_usage(model)
            usage["requests"] += 1
            usage["input_tokens"] += input_tokens
            usage["output_tokens"] += output_tokens
            usage["total_tokens"] += input_tokens + output_tokens
            usage["last_used"] = datetime.now().isoformat()
            
            # 更新当前日期
            self.usage_data["current_date"] = self._get_today_key()
            
            self._save_usage_data()
    
    def get_daily_stats(self, model: Optional[str] = None) -> Dict:
        """
        获取每日统计信息
        
        Args:
            model: 模型名称，如果为None则返回所有模型的统计
            
        Returns:
            统计信息字典
        """
        today = self._get_today_key()
        stats = {}
        
        models_to_check = [model] if model else self.model_limits.keys()
        
        for m in models_to_check:
            usage = self._get_model_usage(m)
            limit = self.model_limits.get(m, {})
            
            stats[m] = {
                "requests": usage["requests"],
                "limit": limit.get("rpd", 0),
                "usage_percent": (usage["requests"] / limit.get("rpd", 1)) * 100 if limit.get("rpd") else 0,
                "input_tokens": usage["input_tokens"],
                "output_tokens": usage["output_tokens"],
                "total_tokens": usage["total_tokens"],
                "tpm_limit": limit.get("tpm", 0),
                "last_used": usage.get("last_used", "N/A")
            }
        
        return {
            "date": today,
            "models": stats
        }


# 全局用量监控器实例
usage_monitor = UsageMonitor()

