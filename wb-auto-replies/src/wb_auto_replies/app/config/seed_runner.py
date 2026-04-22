from __future__ import annotations

import argparse
from typing import Sequence

from wb_auto_replies.app.db.session import SessionLocal
from wb_auto_replies.app.config.seeds import SeedService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wb-auto-replies-seed")
    parser.add_argument("--shop-name", required=True)
    parser.add_argument("--wb-token", required=True)
    parser.add_argument("--mode", default="draft", choices=["backfill", "draft", "publish"])
    parser.add_argument("--gpt-model", default="gpt-4.1-mini")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    service = SeedService()
    with SessionLocal() as db:
        shop = service.upsert_shop(
            db,
            shop_name=args.shop_name,
            wb_token=args.wb_token,
            mode=args.mode,
            gpt_model=args.gpt_model,
        )
        service.seed_karmic_rules(db, shop)
        service.seed_semantic_templates(db, shop)
        db.commit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
