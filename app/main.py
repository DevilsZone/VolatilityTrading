"""
app/main.py
"""

import argparse
from pathlib import Path

from app.config import AppConfig
from app.runner_factory import RunnerFactory


BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_PATH_DUMMY = BASE_DIR / "config" / "settings_dummy.yaml"
SETTINGS_PATH_LIVE = BASE_DIR / "config" / "settings_live.yaml"
SETTINGS_PATH_BACKTEST = BASE_DIR / "config" / "settings_backtest.yaml"

def parse_args():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["dummy", "backtest", "live"], default="dummy")
    return parser.parse_args()


def main():
    """
    Main function
    """
    args = parse_args()

    # Load config dynamically
    path = str(SETTINGS_PATH_DUMMY)
    if args.mode == "dummy":
        path = str(SETTINGS_PATH_DUMMY)
    if args.mode == "backtest":
        path = str(SETTINGS_PATH_BACKTEST)
    if args.mode == "live":
        path = str(SETTINGS_PATH_LIVE)
    config = AppConfig.from_yaml(path=path)

    engine = RunnerFactory.build(config)
    engine.run()


if __name__ == "__main__":
    main()