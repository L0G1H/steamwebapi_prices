import requests
import pandas as pd
import numpy as np


def get_prices(api_key: str, *, game: str = "cs2", currency: str = "EUR", return_type: str = "dataframe") -> dict or pd.DataFrame:
    allowed_games = {"cs2": "csgo", "dota2": "dota", "rust": "rust", "tf2": "tf2"}
    games_codes = {"cs2": 730, "dota2": 570, "rust": 252490, "tf2": 440}

    game = game.lower()
    currency = currency.upper()
    return_type = return_type.lower()

    if return_type not in {"dataframe", "dict"}:
        raise ValueError("Invalid 'return_type'. Use 'dataframe' or 'dict'.")

    if game not in allowed_games.keys():
        games_str = "', '".join(allowed_games.keys())
        raise ValueError(f"Invalid 'game'. Use one of the following values: '{games_str}'.")

    response = requests.get("https://www.steamwebapi.com/steam/api/items",
                            params={"key": api_key, "game": allowed_games[game], "currency": currency})

    try:
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as http_err:
        raise SystemExit(f"HTTP error occurred: {http_err}")
    except ValueError as json_err:
        raise SystemExit(f"JSON decoding failed: {json_err}")
    except Exception as err:
        raise SystemExit(f"An unexpected error occurred: {err}")

    df = pd.DataFrame(data).set_index("markethashname").fillna(0).infer_objects(copy=False)
    df = df.loc[~df.index.duplicated()]
    df = df.reset_index()

    df = df.replace(0, np.nan)

    df["game"] = game
    df["game_code"] = games_codes[game]

    filtered_df = df[(df["pricereal24h"] > 0) & (df["pricereal7d"] > 0) & (df["pricereal"] > 0) &
                     (df["pricereal30d"] > 0) & (df["pricereal90d"] > 0)]

    market_shift = {
        "pricereal": 1,
        "pricereal24h": np.mean(filtered_df["pricereal"] / filtered_df["pricereal24h"]),
        "pricereal7d": np.mean(filtered_df["pricereal"] / filtered_df["pricereal7d"]),
        "pricereal30d": np.mean(filtered_df["pricereal"] / filtered_df["pricereal30d"]),
        "pricereal90d": np.mean(filtered_df["pricereal"] / filtered_df["pricereal90d"])
    }

    df["real_price"] = np.nan

    for col, ratio in market_shift.items():
        mask = (~df[col].isna()) & (df[col] > 0) & (df["real_price"].isna())
        df.loc[mask, "real_price"] = round(df.loc[mask, col] * ratio, 2)

    min_cols = ["buyorderprice", "pricemin"]

    df["steam_price_min"] = 0.0

    for col in min_cols:
        mask = (~df[col].isna()) & (df[col] > 0) & (df["steam_price_min"] < df[col])
        df.loc[mask, "steam_price_min"] = df.loc[mask, col]

    max_cols = ["pricemedian", "priceavg", "pricemax", "pricemax"]

    df["steam_price_max"] = float("inf")

    for col in max_cols:
        mask = (~df[col].isna()) & (df[col] > 0) & (df["steam_price_max"] > df[col])
        df.loc[mask, "steam_price_max"] = df.loc[mask, col]

    df["steam_price"] = np.where((df["steam_price_min"] != 0) & (df["steam_price_max"] != float("inf")),
                                 round((df["steam_price_min"] + df["steam_price_max"]) / 2, 2),
                                 np.nan)

    df["steam_price_taxed"] = np.where(~pd.isna(df["steam_price"]),
                                       np.round(df["steam_price"] / 1.15 - 0.0119, 2),
                                       np.nan)

    filtered_df = df[(~df["steam_price"].isna()) & (~df["real_price"].isna())].copy()
    filtered_df["ratio"] = df["steam_price"] / df["real_price"]
    ratio = filtered_df["ratio"].mean()
    inverse_ratio = 1 / ratio

    df["estimated_steam_price"] = np.where(~df["real_price"].isna(),
                                           round(df["real_price"] * ratio),
                                           np.nan)

    df["estimated_steam_price_taxed"] = np.where(~pd.isna(df["estimated_steam_price"]),
                                                 np.round(df["estimated_steam_price"] / 1.15 - 0.0119, 2),
                                                 np.nan)


    df["estimated_real_price"] = np.where(~df["steam_price"].isna(),
                                          round(df["steam_price"] * inverse_ratio),
                                          np.nan)

    df = df.rename(columns={"sold24h": "steam_sold_24h", "sold7d": "steam_sold_7d", "sold30d": "steam_sold_30d",
                            "sold90d": "steam_sold_90d", "itemimage": "image", "markethashname": "name",
                            "pricerealchangepercent24h": "real_price_change_percent_24h",
                            "pricerealchangepercent7d": "real_price_change_percent_7d",
                            "pricerealchangepercent30d": "real_price_change_percent_30d",
                            "pricerealchangepercent90d": "real_price_change_percent_90d"})

    df = df[["name", "game", "game_code", "steam_price", "steam_price_taxed", "estimated_steam_price",
             "estimated_steam_price_taxed", "steam_sold_24h", "steam_sold_7d", "steam_sold_30d", "steam_sold_90d",
             "real_price", "estimated_real_price", "real_price_change_percent_24h", "real_price_change_percent_7d",
             "real_price_change_percent_30d", "real_price_change_percent_90d"]]

    if return_type == "dataframe":
        return df

    if return_type == "dict":
        df = df.set_index("name")
        return df.to_dict(orient="index")