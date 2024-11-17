import steam_prices
import os
import pandas as pd


dfs = []

for game in ["cs2", "dota2", "rust", "tf2"]:
    df = steam_prices.get_prices(
        os.getenv("steam_web_api"),
        game=game,
        currency="EUR",
        return_type="dataframe"
    )
    dfs.append(df)

full_df = pd.concat(dfs, ignore_index=True)

full_df.to_csv("steam_prices.csv", index=False)

full_df.info()
