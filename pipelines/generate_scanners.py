import pandas as pd
from pathlib import Path

INPUT_FILE = "data/parquet/growth_scored.parquet"

OUTPUT_DIR = Path("data/processed/scanners")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if not Path(INPUT_FILE).exists():

    print(f"Missing file: {INPUT_FILE}")

    exit()

df = pd.read_parquet(INPUT_FILE)

required_cols = [
    "symbol",
    "institutional_score",
    "smart_money_score",
    "breakout_score",
    "volume_score",
    "momentum_score",
]

for col in required_cols:

    if col not in df.columns:
        df[col] = 0

top_institutional = (
    df.sort_values(
        "institutional_score",
        ascending=False
    )
    .head(25)
)

smart_money = (
    df.sort_values(
        "smart_money_score",
        ascending=False
    )
    .head(25)
)

breakouts = (
    df.sort_values(
        "breakout_score",
        ascending=False
    )
    .head(25)
)

momentum = (
    df.sort_values(
        "momentum_score",
        ascending=False
    )
    .head(25)
)

volume = (
    df.sort_values(
        "volume_score",
        ascending=False
    )
    .head(25)
)

top_institutional.to_csv(
    OUTPUT_DIR / "top_institutional.csv",
    index=False
)

smart_money.to_csv(
    OUTPUT_DIR / "smart_money.csv",
    index=False
)

breakouts.to_csv(
    OUTPUT_DIR / "breakouts.csv",
    index=False
)

momentum.to_csv(
    OUTPUT_DIR / "momentum.csv",
    index=False
)

volume.to_csv(
    OUTPUT_DIR / "volume_expansion.csv",
    index=False
)

print("SCANNERS GENERATED SUCCESSFULLY")
