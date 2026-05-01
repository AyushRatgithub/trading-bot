"""
validators.py – CLI input validation helpers.

All functions raise ``ValueError`` with a human-readable message on bad input.
"""

from __future__ import annotations

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}  # STOP_MARKET = bonus


def validate_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s or not s.isalnum():
        raise ValueError(
            f"Invalid symbol '{symbol}'. Must be alphanumeric (e.g. BTCUSDT)."
        )
    return s


def validate_side(side: str) -> str:
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValueError(
            f"Invalid side '{side}'. Choose from: {', '.join(sorted(VALID_SIDES))}."
        )
    return s


def validate_order_type(order_type: str) -> str:
    t = order_type.strip().upper()
    if t not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. "
            f"Choose from: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return t


def validate_quantity(quantity: str | float) -> float:
    try:
        q = float(quantity)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if q <= 0:
        raise ValueError(f"Quantity must be > 0 (got {q}).")
    return q


def validate_price(price: str | float | None, *, required: bool = False) -> float | None:
    if price is None or price == "":
        if required:
            raise ValueError("Price is required for LIMIT and STOP_MARKET orders.")
        return None
    try:
        p = float(price)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid price '{price}'. Must be a positive number.")
    if p <= 0:
        raise ValueError(f"Price must be > 0 (got {p}).")
    return p


def validate_stop_price(stop_price: str | float | None, *, required: bool = False) -> float | None:
    if stop_price is None or stop_price == "":
        if required:
            raise ValueError("Stop price is required for STOP_MARKET orders.")
        return None
    try:
        sp = float(stop_price)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid stop price '{stop_price}'. Must be a positive number.")
    if sp <= 0:
        raise ValueError(f"Stop price must be > 0 (got {sp}).")
    return sp
