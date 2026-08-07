"""
config_loader.py - 設定檔載入模組
"""
import yaml
import os

def load_config(path: str = 'config.yaml') -> dict:
    """載入並驗證 config.yaml。"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"找不到設定檔：{path}，請先複製 config.example.yaml 並填寫設定。")
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config
