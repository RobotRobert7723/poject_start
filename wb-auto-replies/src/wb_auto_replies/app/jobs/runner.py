from __future__ import annotations

import argparse
from typing import Sequence

from wb_auto_replies.app.jobs.service import JobService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wb-auto-replies")
    subparsers = parser.add_subparsers(dest="command", required=True)

    backfill = subparsers.add_parser("backfill")
    backfill.add_argument("--shop-id", type=int, required=True)

    draft = subparsers.add_parser("draft")
    draft.add_argument("--shop-id", type=int, required=True)

    publish = subparsers.add_parser("publish")
    publish.add_argument("--shop-id", type=int, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    service = JobService()

    if args.command == "backfill":
        service.run_backfill(shop_id=args.shop_id)
    elif args.command == "draft":
        service.run_draft(shop_id=args.shop_id)
    elif args.command == "publish":
        service.run_publish(shop_id=args.shop_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
