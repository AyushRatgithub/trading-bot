"""
client.py – Low-level Binance Futures Testnet REST client.
Handles HMAC-SHA256 signing, timestamp injection, and raw HTTP calls.
"""

import hashlib
import hmac
import time
import logging
from urllib.parse import urlencode

import httpx

from .logging_config import get_logger

logger = get_logger(__name__)

BASE_URL = "https://testnet.binancefuture.com"


class BinanceClient:
    """Thin wrapper around the Binance Futures Testnet REST API."""

    def __init__(self, api_key: str, api_secret: str, base_url: str = BASE_URL):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self._http = httpx.Client(
            base_url=self.base_url,
            headers={"X-MBX-APIKEY": self.api_key},
            timeout=15.0,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sign(self, params: dict) -> dict:
        """Append a timestamp and HMAC-SHA256 signature to *params* (in-place)."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(self, method: str, path: str, signed: bool = False, **kwargs) -> dict:
        """
        Execute an HTTP request and return the parsed JSON body.

        Raises
        ------
        httpx.HTTPStatusError   – non-2xx response from the exchange
        httpx.RequestError      – network-level failure
        """
        params = kwargs.pop("params", {}) or {}
        if signed:
            params = self._sign(params)

        logger.debug("→ %s %s  params=%s", method.upper(), path, params)

        try:
            response = self._http.request(method, path, params=params, **kwargs)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "API error %s %s: %s",
                exc.response.status_code,
                path,
                exc.response.text,
            )
            raise
        except httpx.RequestError as exc:
            logger.error("Network failure calling %s: %s", path, exc)
            raise

        data = response.json()
        logger.debug("← %s %s  response=%s", method.upper(), path, data)
        return data

    # ------------------------------------------------------------------
    # Public API helpers
    # ------------------------------------------------------------------

    def get_exchange_info(self) -> dict:
        """Return exchange information (symbol rules, filters, etc.)."""
        return self._request("GET", "/fapi/v1/exchangeInfo")

    def get_account(self) -> dict:
        """Return account information (balances, positions)."""
        return self._request("GET", "/fapi/v2/account", signed=True, params={})

    def place_order(self, **order_params) -> dict:
        """
        Place a new futures order.

        Parameters are forwarded verbatim to POST /fapi/v1/order (signed).
        Common keys: symbol, side, type, quantity, price, timeInForce,
                     stopPrice, reduceOnly, newOrderRespType.
        """
        logger.info("Placing order: %s", order_params)
        return self._request(
            "POST",
            "/fapi/v1/order",
            signed=True,
            params=order_params,
        )

    def cancel_order(self, symbol: str, order_id: int) -> dict:
        """Cancel an open order by orderId."""
        return self._request(
            "DELETE",
            "/fapi/v1/order",
            signed=True,
            params={"symbol": symbol, "orderId": order_id},
        )

    def close(self):
        """Release the underlying HTTP connection pool."""
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
