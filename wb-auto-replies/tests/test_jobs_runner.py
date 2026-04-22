from wb_auto_replies.app.jobs.runner import build_parser


def test_runner_parses_backfill_command() -> None:
    parser = build_parser()
    args = parser.parse_args(["backfill", "--shop-id", "1", "--take", "10", "--skip", "0"])

    assert args.command == "backfill"
    assert args.shop_id == 1
    assert args.take == 10
    assert args.skip == 0


def test_runner_parses_publish_command() -> None:
    parser = build_parser()
    args = parser.parse_args(["publish", "--shop-id", "2"])

    assert args.command == "publish"
    assert args.shop_id == 2
