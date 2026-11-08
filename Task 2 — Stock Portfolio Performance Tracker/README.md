## Task 2: Stock Portfolio Performance Tracker

A Python command-line application for tracking stock holdings,
calculating portfolio returns, and saving performance reports.

### Features

- Stock ticker validation using a company constituents CSV
- Offline demonstration prices and optional live price retrieval
- Portfolio positions stored in a dictionary
- Weighted average purchase cost for repeated stock entries
- Per-holding and overall profit/loss calculations
- Percentage return calculations
- Persistent CSV performance logs

### Files

- `portfolio.py` - Main application
- `constituents.csv` - Company and ticker reference
- `sample_prices.csv` - Illustrative offline prices
- `portfolio_summary.csv` - Generated performance reports
- `requirements.txt` - Optional live-price dependency

### Run

```bash
python portfolio.py
```

For live quotes, install the optional dependency:

```bash
python -m pip install yfinance
```

### Financial Calculation

Invested Capital = Purchase Price × Number of Shares

Market Value = Current Price × Number of Shares

Profit/Loss = Market Value - Invested Capital

Return (%) = (Profit/Loss / Invested Capital) × 100

### Limitations

Sample prices are fictional and must not be used for investment
decisions. Live quotes depend on the external data provider.
This educational tool excludes brokerage fees, taxes, and dividends.