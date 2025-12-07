# app/config.py

from dataclasses import dataclass
from typing import Literal, List, cast
import os
import yaml


ModeType = Literal["dummy", "backtest", "live"]


@dataclass
class AppConfig:
    mode: ModeType = "dummy"

    api_key: str = ""
    access_token: str = ""

    instruments: List[int] = None

    backtest_start: str = "2024-10-01"
    backtest_end: str = "2024-10-07"
    backtest_interval: str = "minute"

    @staticmethod
    def from_yaml(path: str) -> "AppConfig":
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}

        raw_mode: str = data.get("mode", "dummy")

        if raw_mode not in ("dummy", "backtest", "live"):
            raise ValueError(f"Invalid mode in config/CLI: {raw_mode}")

        mode: ModeType = cast(ModeType, raw_mode)

        zerodha = data.get("zerodha", {})
        universe = data.get("universe", {})
        backtest = data.get("backtest", {})

        api_key = os.getenv("ZERODHA_API_KEY", zerodha.get("api_key", ""))
        access_token = os.getenv("ZERODHA_ACCESS_TOKEN", zerodha.get("access_token", ""))

        instruments = universe.get("instruments", [256265])

        return AppConfig(
            mode=mode,
            api_key=api_key,
            access_token=access_token,
            instruments=instruments,
            backtest_start=backtest.get("start", "2024-10-01"),
            backtest_end=backtest.get("end", "2024-10-07"),
            backtest_interval=backtest.get("interval", "minute"),
        )
