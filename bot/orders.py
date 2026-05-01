"""
orders.py – High-level order placement logic.

Sits between the CLI layer and the raw BinanceClient.
Returns a structured OrderResult dataclass so the CLI can display it uniformly.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from .client import BinanceClient
from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class OrderResult:
    success: bool
    order_id: Optional[int] = None
    symbol: Optional[str] = None
    side: Optional[str] = None
    order_type: Optional[str] = None
    status: Optional[str] = None
    executed_qty: Optional[str] = None
    avg_price: Optional[str] = None
    price: Optional[str] = None
    orig_qty: Optional[str] = None
    raw_response: dict = field(default_factory=dict)
    error_message: Optional[str] = None

    # ------------------------------------------------------------------ #
    @classmethod
    def from_response(cls, data: dict) -> "OrderResult":
        return cls(
            success=True,
            order_id=data.get("orderId"),
            symbol=data.get("symbol"),
            side=data.get("side"),
            order_type=data.get("type"),
            status=data.get("status"),
            executed_qty=data.get("executedQty"),
            avg_price=data.get("avgPrice"),
            price=data.get("price"),
            orig_qty=data.get("origQty"),
            raw_response=data,
        )

    @classmethod
    def from_error(cls, message: str) -> "OrderResult":
        return cls(success=False, error_message=message)


# ------------------------------------------------------------------ #
# Public helpers
# ------------------------------------------------------------------ #

def place_market_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
) -> OrderResult:
    """Place a MARKET order."""
    params = dict(
        symbol=symbol,
        side=side,
        type="MARKET",
        quantity=quantity,
        newOrderRespType="RESULT",
    )
    logger.info(
        "Market order request → symbol=%s side=%s qty=%s",
        symbol, side, quantity,
    )
    try:
        data = client.place_order(**params)
        result = OrderResult.from_response(data)
        logger.info(
            "Market order accepted ← orderId=%s status=%s executedQty=%s avgPrice=%s",
            result.order_id, result.status, result.executed_qty, result.avg_price,
        )
        return result
    except Exception as exc:
        logger.error("Market order failed: %s", exc)
        return OrderResult.from_error(str(exc))


def place_limit_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    time_in_force: str = "GTC",
) -> OrderResult:
    """Place a LIMIT order."""
    params = dict(
        symbol=symbol,
        side=side,
        type="LIMIT",
        quantity=quantity,
        price=price,
        timeInForce=time_in_force,
        newOrderRespType="RESULT",
    )
    logger.info(
        "Limit order request → symbol=%s side=%s qty=%s price=%s tif=%s",
        symbol, side, quantity, price, time_in_force,
    )
    try:
        data = client.place_order(**params)
        result = OrderResult.from_response(data)
        logger.info(
            "Limit order accepted ← orderId=%s status=%s",
            result.order_id, result.status,
        )
        return result
    except Exception as exc:
        logger.error("Limit order failed: %s", exc)
        return OrderResult.from_error(str(exc))


def place_stop_market_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    stop_price: float,
) -> OrderResult:
    """Place a STOP_MARKET order (bonus order type)."""
    params = dict(
        symbol=symbol,
        side=side,
        type="STOP_MARKET",
        quantity=quantity,
        stopPrice=stop_price,
        newOrderRespType="RESULT",
    )
    logger.info(
        "Stop-Market order request → symbol=%s side=%s qty=%s stopPrice=%s",
        symbol, side, quantity, stop_price,
    )
    try:
        data = client.place_order(**params)
        result = OrderResult.from_response(data)
        logger.info(
            "Stop-Market order accepted ← orderId=%s status=%s",
            result.order_id, result.status,
        )
        return result
    except Exception as exc:
        logger.error("Stop-Market order failed: %s", exc)
        return OrderResult.from_error(str(exc))
