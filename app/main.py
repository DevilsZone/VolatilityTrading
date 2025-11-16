# app/main.py

import argparse
from app.config import AppConfig
from app.runner_factory import RunnerFactory


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["dummy", "backtest", "live"], default="dummy")
    return parser.parse_args()


def main():
    args = parse_args()

    # Load config dynamically
    config = AppConfig(mode=args.mode)

    engine = RunnerFactory.build(config)
    engine.run()


if __name__ == "__main__":
    main()