"""
cli.py – Command-line interface for the Binance Futures Testnet trading bot.

Usage examples:
    python -m bot.cli place --symbol BTCUSDT --side BUY --type MARKET --qty 0.01
    python -m bot.cli place --symbol BTCUSDT --side SELL --type LIMIT --qty 0.01 --price 90000
    python -m bot.cli place --symbol BTCUSDT --side SELL --type STOP_MARKET --qty 0.01 --stop-price 85000
"""

from __future__ import annotations

import argparse
import os
import sys
import textwrap

from .client import BinanceClient
from .logging_config import get_logger, setup_logging
from .orders import (
    OrderResult,
    place_limit_order,
    place_market_order,
    place_stop_market_order,
)
from .validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)

logger = get_logger(__name__)

# ------------------------------------------------------------------ #
# Pretty-print helpers
# ------------------------------------------------------------------ #

SEPARATOR = "─" * 56


def _section(title: str) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def _print_request_summary(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None,
    stop_price: float | None = None,
) -> None:
    _section("ORDER REQUEST SUMMARY")
    print(f"  Symbol     : {symbol}")
    print(f"  Side       : {side}")
    print(f"  Order Type : {order_type}")
    print(f"  Quantity   : {quantity}")
    if price is not None:
        print(f"  Price      : {price}")
    if stop_price is not None:
        print(f"  Stop Price : {stop_price}")


def _print_order_result(result: OrderResult) -> None:
    if result.success:
        _section("ORDER RESPONSE")
        print(f"  Order ID     : {result.order_id}")
        print(f"  Symbol       : {result.symbol}")
        print(f"  Side         : {result.side}")
        print(f"  Type         : {result.order_type}")
        print(f"  Status       : {result.status}")
        print(f"  Orig Qty     : {result.orig_qty}")
        print(f"  Executed Qty : {result.executed_qty}")
        if result.avg_price and result.avg_price != "0":
            print(f"  Avg Price    : {result.avg_price}")
        if result.price and result.price != "0":
            print(f"  Limit Price  : {result.price}")
        print(f"\n  ✅  Order placed successfully!\n")
    else:
        _section("ORDER FAILED")
        print(f"  ❌  {result.error_message}\n")


# ------------------------------------------------------------------ #
# Build argument parser
# ------------------------------------------------------------------ #

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading-bot",
        description="Binance Futures Testnet – simple trading bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Examples:
              # Market BUY
              python -m bot.cli place --symbol BTCUSDT --side BUY --type MARKET --qty 0.01

              # Limit SELL
              python -m bot.cli place --symbol BTCUSDT --side SELL --type LIMIT --qty 0.01 --price 90000

              # Stop-Market SELL (bonus)
              python -m bot.cli place --symbol BTCUSDT --side SELL --type STOP_MARKET --qty 0.01 --stop-price 85000

            API credentials are read from env vars:
              BINANCE_API_KEY   – your testnet API key
              BINANCE_API_SECRET – your testnet API secret
            """
        ),
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # ---------- place ----------
    place = sub.add_parser("place", help="Place a new futures order")
    place.add_argument(
        "--symbol", required=True,
        help="Trading pair, e.g. BTCUSDT",
    )
    place.add_argument(
        "--side", required=True, choices=["BUY", "SELL"],
        help="Order side",
    )
    place.add_argument(
        "--type", dest="order_type", required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        help="Order type",
    )
    place.add_argument(
        "--qty", dest="quantity", required=True, type=float,
        help="Order quantity (base asset)",
    )
    place.add_argument(
        "--price", type=float, default=None,
        help="Limit price (required for LIMIT orders)",
    )
    place.add_argument(
        "--stop-price", dest="stop_price", type=float, default=None,
        help="Stop trigger price (required for STOP_MARKET orders)",
    )
    place.add_argument(
        "--tif", default="GTC",
        choices=["GTC", "IOC", "FOK", "GTX"],
        help="Time-in-force for LIMIT orders (default: GTC)",
    )

    return parser


# ------------------------------------------------------------------ #
# Main
# ------------------------------------------------------------------ #

def main() -> None:
    setup_logging()
    parser = _build_parser()
    args = parser.parse_args()

    # --- Load credentials from environment ---
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        print(
            "\n❌  Missing credentials.\n"
            "   Set environment variables:\n"
            "     export BINANCE_API_KEY=<your_key>\n"
            "     export BINANCE_API_SECRET=<your_secret>\n"
        )
        sys.exit(1)

    # --- Validate inputs ---
    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        quantity = validate_quantity(args.quantity)

        price = None
        stop_price = None

        if order_type == "LIMIT":
            price = validate_price(args.price, required=True)
        elif order_type == "STOP_MARKET":
            stop_price = validate_stop_price(args.stop_price, required=True)

    except ValueError as exc:
        print(f"\n❌  Validation error: {exc}\n")
        logger.warning("Validation error: %s", exc)
        sys.exit(1)

    # --- Print request summary ---
    _print_request_summary(symbol, side, order_type, quantity, price, stop_price)

    # --- Execute order ---
    with BinanceClient(api_key, api_secret) as client:
        if order_type == "MARKET":
            result = place_market_order(client, symbol, side, quantity)
        elif order_type == "LIMIT":
            result = place_limit_order(client, symbol, side, quantity, price, args.tif)
        else:  # STOP_MARKET
            result = place_stop_market_order(client, symbol, side, quantity, stop_price)

    # --- Display result ---
    _print_order_result(result)

    if not result.success:
        sys.exit(1)


if __name__ == "__main__":
    main()
