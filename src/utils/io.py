"""公共 I/O 与配置加载工具。所有模块统一从这里加载 config,避免路径硬编码。"""
from __future__ import annotations

from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "configs" / "config.yaml"


def load_config(path: Path | str = CONFIG_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_path(rel: str) -> Path:
    """把 config 里的相对路径解析成绝对路径。"""
    return (PROJECT_ROOT / rel).resolve()
