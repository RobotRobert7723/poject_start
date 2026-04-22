from __future__ import annotations

import argparse
from typing import Sequence

from wb_auto_replies.app.jobs.service import JobService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wb-auto-replies")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("backfill", "draft", "publish"):
        job = subparsers.add_parser(command)
        job.add_argument("--shop-id", type=int, required=True)
        job.add_argument("--take", type=int, default=50)
        job.add_argument("--skip", type=int, default=0)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    service = JobService()

    if args.command == "backfill":
        service.run_backfill(shop_id=args.shop_id, take=args.take, skip=args.skip)
    elif args.command == "draft":
        service.run_draft(shop_id=args.shop_id, take=args.take, skip=args.skip)
    elif args.command == "publish":
        service.run_publish(shop_id=args.shop_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
