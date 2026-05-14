from core.market_data import load_parquet
from core.indicators import add_indicators

df = load_parquet("market_data.parquet")

symbol_df = df[df["symbol"] == "RELIANCE.NS"]

symbol_df = add_indicators(symbol_df)

print(symbol_df.tail())