import json
from pathlib import Path

import pandas as pd
from tradingview_screener import Query

cols = ["name", "description", "close"]
all_dfs = []
offset = 0
batch = 50

while True:
    q = Query().select(*cols).set_markets("nigeria")
    q.query["range"] = [offset, offset + batch]
    count, df = q.get_scanner_data()

    if df.empty:
        break

    all_dfs.append(df)
    offset += batch

    if offset >= count:
        break

df = pd.concat(all_dfs, ignore_index=True)

# Keep only what we need: ticker → name mapping
stocks = df[["ticker", "name", "description"]].to_dict(orient="records")

parent = Path(__file__).parent.resolve()
with open(f"{parent}/nigerian_stocks.json", "w") as f:
    json.dump(stocks, f, indent=2)

print(f"Saved {len(stocks)} stocks to nigerian_stocks.json")