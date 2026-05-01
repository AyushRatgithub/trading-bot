# Binance Futures Testnet – Trading Bot

A clean, modular Python CLI for placing orders on the **Binance Futures Testnet (USDT-M)**.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST client (signing, HTTP)
│   ├── orders.py          # Order placement logic + OrderResult dataclass
│   ├── validators.py      # Input validation helpers
│   ├── logging_config.py  # Rotating file + console log setup
│   └── cli.py             # argparse CLI entry point
├── logs/
│   └── trading_bot.log    # Auto-created on first run
├── README.md
└── requirements.txt
```

---

## Setup

### 1 – Prerequisites

- Python **3.9+**
- A [Binance Futures Testnet](https://testnet.binancefuture.com) account

### 2 – Get Testnet API Credentials

1. Go to <https://testnet.binancefuture.com>
2. Log in / register
3. Under **API Key**, generate a new key pair
4. Copy your **API Key** and **Secret Key**

### 3 – Install Dependencies

```bash
cd trading_bot
pip install -r requirements.txt
```

### 4 – Set Environment Variables

```bash
# Linux / macOS
export BINANCE_API_KEY="your_testnet_api_key"
export BINANCE_API_SECRET="your_testnet_api_secret"

# Windows (PowerShell)
$env:BINANCE_API_KEY="your_testnet_api_key"
$env:BINANCE_API_SECRET="your_testnet_api_secret"
```

---

## How to Run

### General syntax

```bash
python -m bot.cli place \
  --symbol  <SYMBOL>     \   # e.g. BTCUSDT
  --side    BUY|SELL     \
  --type    MARKET|LIMIT|STOP_MARKET \
  --qty     <QUANTITY>   \
  [--price  <PRICE>]     \   # Required for LIMIT
  [--stop-price <PRICE>] \   # Required for STOP_MARKET
  [--tif    GTC|IOC|FOK]     # Optional, default GTC
```

---

### Examples

#### Market BUY

```bash
python -m bot.cli place --symbol BTCUSDT --side BUY --type MARKET --qty 0.01
```

**Output:**
```
────────────────────────────────────────────────────────
  ORDER REQUEST SUMMARY
────────────────────────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : BUY
  Order Type : MARKET
  Quantity   : 0.01

────────────────────────────────────────────────────────
  ORDER RESPONSE
────────────────────────────────────────────────────────
  Order ID     : 3847201938
  Symbol       : BTCUSDT
  Side         : BUY
  Type         : MARKET
  Status       : FILLED
  Orig Qty     : 0.01
  Executed Qty : 0.01
  Avg Price    : 96432.10

  ✅  Order placed successfully!
```

#### Limit SELL

```bash
python -m bot.cli place --symbol BTCUSDT --side SELL --type LIMIT --qty 0.01 --price 99000
```

#### Limit BUY with IOC time-in-force

```bash
python -m bot.cli place --symbol ETHUSDT --side BUY --type LIMIT --qty 0.1 --price 3200 --tif IOC
```

#### Stop-Market SELL (bonus order type)

```bash
python -m bot.cli place --symbol BTCUSDT --side SELL --type STOP_MARKET --qty 0.01 --stop-price 85000
```

---

## Logging

All activity is written to **`logs/trading_bot.log`** (auto-created).

| Level   | Destination       | Content |
|---------|-------------------|---------|
| DEBUG   | File only         | Full request params & raw API responses |
| INFO    | File + console    | Order intent and outcomes |
| WARNING | File + console    | Validation failures |
| ERROR   | File + console    | API errors, network failures |

The log file rotates at **5 MB** and keeps **3** backups.

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Missing `--price` for LIMIT | Validation error before any API call |
| Invalid symbol characters | Validation error before any API call |
| `BINANCE_API_KEY` not set | Clear message, exit code 1 |
| 4xx API error (bad symbol, etc.) | Error logged + printed, exit code 1 |
| Network timeout / DNS failure | `httpx.RequestError` caught, logged, exit code 1 |

---

## Assumptions

- Only **USDT-M** perpetual futures are targeted (base URL: `https://testnet.binancefuture.com`).
- Quantity is in **base asset units** (e.g. BTC for BTCUSDT).
- The testnet does **not** require an active position to place a STOP_MARKET order; exchange-side margin rules still apply.
- Credentials are supplied via environment variables (not hard-coded or CLI flags for security).

---

## Bonus Feature

**STOP_MARKET** orders are implemented as the third order type.  
Use `--type STOP_MARKET --stop-price <TRIGGER_PRICE>`.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `httpx` | Async-ready HTTP client (sync mode used here) |

No `python-binance` wrapper – direct REST calls keep the dependency footprint minimal and make the API layer transparent.
