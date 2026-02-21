"""
stock_agents.py

Simple agents for checking stock prices on Yahoo Finance using the `yfinance` library.

Features:
- StockAgent class with methods to get the latest price and historical data
- CLI for quick use: `quote` and `history` commands
- Safe import behavior: instructs the user to pip-install yfinance if missing
- Optional helper to expose simple functions that can be wrapped as tools

Notes:
- This script does not perform any network-restricted actions at write time. It defines code
  that will use the network when executed (to contact Yahoo Finance) — you must run it in
  an environment with network access and (optionally) install `yfinance`.

Usage examples:
    python stock_agents.py quote AAPL
    python stock_agents.py history TSLA --period 7d

"""
from __future__ import annotations

import argparse
import datetime as dt
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    import yfinance as yf
except Exception:  # keep the error visible to the user (no silent failures)
    yf = None


def _ensure_yfinance_available() -> None:
    """Raise a helpful error if yfinance is not installed.

    We avoid importing or installing packages automatically here. The caller should
    run `pip install yfinance` if this raises.
    """
    if yf is None:
        raise ImportError(
            "The 'yfinance' package is required. Install with: pip install yfinance"
        )


@dataclass
class Quote:
    symbol: str
    short_name: Optional[str]
    currency: Optional[str]
    regular_market_price: Optional[float]
    previous_close: Optional[float]
    timestamp: Optional[dt.datetime]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "short_name": self.short_name,
            "currency": self.currency,
            "regular_market_price": self.regular_market_price,
            "previous_close": self.previous_close,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class StockAgent:
    """Agent able to fetch stock quotes and history from Yahoo Finance via yfinance.

    Design by contract:
    - get_quote(symbol: str) -> Quote
    - get_history(symbol: str, period: str = "1mo") -> List[Dict[str, Any]]

    The agent does not store state between calls; each method performs a fresh fetch.
    """

    def get_quote(self, symbol: str) -> Quote:
        """Return the latest quote for a ticker symbol.

        Args:
            symbol: Stock ticker symbol (e.g. 'AAPL').

        Returns:
            Quote dataclass with top-level fields filled when available.
        """
        _ensure_yfinance_available()
        if not symbol or not isinstance(symbol, str):
            raise ValueError("symbol must be a non-empty string")

        ticker = yf.Ticker(symbol)
        info = ticker.info if hasattr(ticker, "info") else {}

        # yfinance may provide live price in `fast_info` or `info` depending on version
        regular_market_price = None
        try:
            fast_info = getattr(ticker, "fast_info", None) or {}
            regular_market_price = fast_info.get("last_price") or info.get("regularMarketPrice")
        except Exception:
            # Don't hide errors, but allow fallback to available keys
            regular_market_price = info.get("regularMarketPrice")

        previous_close = info.get("previousClose") or info.get("regularMarketPreviousClose")

        # Timestamp: attempt to obtain the quote timestamp
        timestamp = None
        try:
            # yfinance does not always provide a direct timestamp in `info`.
            # if `regularMarketTime` exists (epoch), convert it.
            rmt = info.get("regularMarketTime")
            if rmt:
                timestamp = dt.datetime.fromtimestamp(rmt)
        except Exception:
            timestamp = None

        return Quote(
            symbol=symbol.upper(),
            short_name=info.get("shortName") or info.get("longName"),
            currency=info.get("currency"),
            regular_market_price=regular_market_price,
            previous_close=previous_close,
            timestamp=timestamp,
        )

    def get_history(self, symbol: str, period: str = "1mo") -> List[Dict[str, Any]]:
        """Return historical OHLCV data for the given symbol.

        Args:
            symbol: Ticker symbol (e.g. 'AAPL').
            period: Data period (e.g. '1d', '5d', '1mo', '3mo', '1y', '5y', 'max') or use
                    interval-based fetch with start/end dates in the future extension.

        Returns:
            A list of rows, each row is a dict with date (ISO string) and open/high/low/close/volume.
        """
        _ensure_yfinance_available()
        if not symbol or not isinstance(symbol, str):
            raise ValueError("symbol must be a non-empty string")

        ticker = yf.Ticker(symbol)
        # The `history` method returns a pandas DataFrame. We convert results to a list of dicts.
        df = ticker.history(period=period)
        records: List[Dict[str, Any]] = []
        if df.empty:
            return records

        # Reset index to get the date in the rows
        df_reset = df.reset_index()
        for _, row in df_reset.iterrows():
            date = row.get("Date")
            # pandas.Timestamp -> ISO string
            date_iso = date.isoformat() if hasattr(date, "isoformat") else str(date)
            records.append(
                {
                    "date": date_iso,
                    "open": _safe_number(row.get("Open")),
                    "high": _safe_number(row.get("High")),
                    "low": _safe_number(row.get("Low")),
                    "close": _safe_number(row.get("Close")),
                    "volume": _safe_number(row.get("Volume")),
                }
            )

        return records


def _safe_number(value: Any) -> Optional[float]:
    """Convert numeric-like values to float when possible, otherwise return None."""
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def create_tools_for_langchain() -> Dict[str, Any]:
    """Return simple callables that can be registered as tools in a tool-using agent/framework.

    This function does not import or depend on langchain. It simply returns plain functions.
    """

    agent = StockAgent()

    def quote_tool(symbol: str) -> Dict[str, Any]:
        """Tool that returns a JSON-serializable dict with quote information."""
        q = agent.get_quote(symbol)
        return q.to_dict()

    def history_tool(symbol: str, period: str = "1mo") -> List[Dict[str, Any]]:
        return agent.get_history(symbol, period=period)

    return {"quote": quote_tool, "history": history_tool}


def _build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Stock agent CLI using yfinance (Yahoo Finance)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_quote = sub.add_parser("quote", help="Get the latest quote for a symbol")
    p_quote.add_argument("symbol", help="Ticker symbol, e.g. AAPL")

    p_hist = sub.add_parser("history", help="Get historical OHLCV for a symbol")
    p_hist.add_argument("symbol", help="Ticker symbol, e.g. TSLA")
    p_hist.add_argument("--period", default="1mo", help="Period string understood by yfinance (default: 1mo)")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_cli()
    args = parser.parse_args(argv)

    agent = StockAgent()

    try:
        if args.command == "quote":
            quote = agent.get_quote(args.symbol)
            print(quote.to_dict())
        elif args.command == "history":
            records = agent.get_history(args.symbol, period=args.period)
            for r in records:
                print(r)
        else:
            parser.print_help()
            return 1

    except ImportError as e:
        # Clear and actionable message
        print(f"Missing dependency: {e}")
        return 2
    except Exception as e:
        # Let unexpected errors surface with a non-zero exit code
        print(f"Error: {e}")
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
