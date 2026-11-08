"""
Stock Portfolio Performance Tracker
-----------------------------------
Enter stock tickers, buy prices and share quantities. The program fetches
current prices (live via yfinance, or manual entry as a fallback), computes
portfolio value and gain/loss per holding, and logs a summary to
portfolio_summary.csv using Python's built-in csv module.

Tickers are validated against constituents.csv (S&P 500 list) when present.

Usage:
    python portfolio.py
"""

import csv
import os
from datetime import datetime

CONSTITUENTS_FILE = "constituents.csv"
SUMMARY_FILE = "portfolio_summary.csv"
SUMMARY_HEADER = [
    "Timestamp", "Ticker", "Company", "Shares", "Buy Price",
    "Current Price", "Invested", "Current Value", "Gain/Loss", "Gain/Loss %",
]


def load_constituents(path: str) -> dict:
    """Load {symbol: company name} from constituents.csv (if available)."""
    companies = {}
    if not os.path.exists(path):
        return companies
    try:
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                companies[row["Symbol"].strip().upper()] = row["Security"].strip()
    except (OSError, KeyError) as exc:
        print(f"Warning: could not read {path} ({exc}). Skipping validation.")
    return companies


def get_live_price(ticker: str):
    """Try to fetch the latest price with yfinance. Returns None on failure."""
    try:
        import yfinance as yf  # optional dependency
        # yfinance uses '-' for share classes, e.g. BRK-B
        data = yf.Ticker(ticker.replace(".", "-")).history(period="1d")
        if not data.empty:
            return float(data["Close"].iloc[-1])
    except Exception:
        pass
    return None


def ask_float(prompt: str, allow_zero: bool = False) -> float:
    """Keep asking until the user enters a valid positive number."""
    while True:
        try:
            value = float(input(prompt).strip())
            if value > 0 or (allow_zero and value == 0):
                return value
            print("  Please enter a positive number.")
        except ValueError:
            print("  Invalid number, try again.")


def collect_positions(companies: dict) -> dict:
    """Prompt the user for holdings. Returns {ticker: {...}}."""
    portfolio = {}
    print("Enter your holdings. Press Enter on an empty ticker to finish.\n")
    while True:
        ticker = input("Ticker symbol: ").strip().upper()
        if not ticker:
            break
        if companies and ticker not in companies:
            print(f"  '{ticker}' not found in {CONSTITUENTS_FILE}. "
                  "Continuing anyway.")
        buy_price = ask_float("  Buy price per share: ")
        shares = ask_float("  Number of shares: ")

        if ticker in portfolio:  # merge repeat purchases (weighted average)
            old = portfolio[ticker]
            total_shares = old["shares"] + shares
            old["buy_price"] = (
                old["buy_price"] * old["shares"] + buy_price * shares
            ) / total_shares
            old["shares"] = total_shares
        else:
            portfolio[ticker] = {"shares": shares, "buy_price": buy_price}
        print(f"  Added {ticker}.\n")
    return portfolio


def fetch_prices(portfolio: dict) -> None:
    """Attach current_price to each position (live, else manual entry)."""
    print("\nFetching current prices...")
    for ticker, pos in portfolio.items():
        price = get_live_price(ticker)
        if price is None:
            print(f"  Live price for {ticker} unavailable.")
            price = ask_float(f"  Enter current price for {ticker}: ")
        pos["current_price"] = price


def calculate(portfolio: dict) -> tuple:
    """Compute per-holding metrics and portfolio totals."""
    total_invested = total_value = 0.0
    for pos in portfolio.values():
        pos["invested"] = pos["buy_price"] * pos["shares"]
        pos["value"] = pos["current_price"] * pos["shares"]
        pos["gain"] = pos["value"] - pos["invested"]
        pos["gain_pct"] = (pos["gain"] / pos["invested"]) * 100
        total_invested += pos["invested"]
        total_value += pos["value"]
    return total_invested, total_value


def print_report(portfolio: dict, companies: dict,
                 total_invested: float, total_value: float) -> None:
    """Print a formatted portfolio table."""
    line = "=" * 86
    print("\n" + line)
    print(f"{'PORTFOLIO SUMMARY':^86}")
    print(line)
    print(f"{'Ticker':<8}{'Shares':>9}{'Buy':>11}{'Current':>11}"
          f"{'Invested':>13}{'Value':>13}{'Gain/Loss':>12}{'%':>9}")
    print("-" * 86)
    for ticker, p in portfolio.items():
        print(f"{ticker:<8}{p['shares']:>9.2f}{p['buy_price']:>11.2f}"
              f"{p['current_price']:>11.2f}{p['invested']:>13.2f}"
              f"{p['value']:>13.2f}{p['gain']:>+12.2f}{p['gain_pct']:>+8.2f}%")
    print("-" * 86)
    total_gain = total_value - total_invested
    total_pct = (total_gain / total_invested) * 100 if total_invested else 0
    print(f"Total invested capital : ${total_invested:,.2f}")
    print(f"Current market value   : ${total_value:,.2f}")
    sign = "+" if total_gain >= 0 else "-"
    print(f"Total gain/loss        : {sign}${abs(total_gain):,.2f} ({total_pct:+.2f}%)")
    print(line)


def log_summary(portfolio: dict, companies: dict, path: str) -> None:
    """Append this run's results to portfolio_summary.csv."""
    new_file = not os.path.exists(path) or os.path.getsize(path) == 0
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if new_file:
                writer.writerow(SUMMARY_HEADER)
            for ticker, p in portfolio.items():
                writer.writerow([
                    timestamp, ticker, companies.get(ticker, "N/A"),
                    f"{p['shares']:.4f}", f"{p['buy_price']:.2f}",
                    f"{p['current_price']:.2f}", f"{p['invested']:.2f}",
                    f"{p['value']:.2f}", f"{p['gain']:.2f}",
                    f"{p['gain_pct']:.2f}",
                ])
        print(f"\nSummary logged to {path}")
    except PermissionError:
        print(f"\nError: cannot write to {path}. Close it if it is open "
              "in another program (e.g. Excel) and try again.")
    except OSError as exc:
        print(f"\nError writing {path}: {exc}")


def main() -> None:
    companies = load_constituents(CONSTITUENTS_FILE)
    portfolio = collect_positions(companies)
    if not portfolio:
        print("No holdings entered. Exiting.")
        return
    fetch_prices(portfolio)
    total_invested, total_value = calculate(portfolio)
    print_report(portfolio, companies, total_invested, total_value)
    log_summary(portfolio, companies, SUMMARY_FILE)


if __name__ == "__main__":
    main()