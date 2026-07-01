"""爬虫配置"""
from dataclasses import dataclass, field


@dataclass
class Config:
    # 延迟（秒）
    delay_min: float = 1.0
    delay_max: float = 3.0

    # 请求超时（秒）
    timeout: int = 30

    # 重试次数
    max_retries: int = 3

    # 浏览器模式
    headless: bool = True

    # 数据存储
    data_dir: str = "data"

    # URL 协议（避免 SSL 警告）
    verify_ssl: bool = True

    # 代理（暂未使用，预留给代理池）
    proxy: str = ""

    # 浏览器复用配置
    reuse_browser: bool = True  # 复用浏览器实例


config = Config()
