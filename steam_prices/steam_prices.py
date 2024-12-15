import requests
import pandas as pd
import numpy as np


def get_prices(api_key: str, *,
               game: str = "cs2",
               currency: str = "EUR",
               return_type: str = "dataframe",
               return_everything: bool = False) -> pd.DataFrame | dict:
    allowed_games = {"cs2": "csgo", "dota2": "dota", "rust": "rust", "tf2": "tf2"}

    game = game.lower()
    currency = currency.upper()
    return_type = return_type.lower()

    if game not in allowed_games:
        raise ValueError(f"Invalid 'game'. Choose from: {', '.join(allowed_games)}")
    if return_type not in {"dataframe", "dict"}:
        raise ValueError("Invalid 'return_type'. Use 'dataframe' or 'dict'.")

    try:
        response = requests.get(
            "https://www.steamwebapi.com/steam/api/items",
            params={"key": api_key, "game": allowed_games[game], "currency": currency}
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        raise SystemExit(f"API request failed: {e}")

    df = pd.DataFrame(data).set_index("markethashname")
    df[df.isna()] = 0

    df = (df.infer_objects(copy=False)
          .reset_index()
          .loc[~df.index.duplicated()]
          .replace(0, np.nan))

    df["steam_price_min"] = df[["buyorderprice", "pricemin"]].max(axis=1, skipna=True)
    df["steam_price_max"] = df[["pricemedian", "priceavg", "pricemax"]].min(axis=1, skipna=True)

    df["steam_price"] = np.where(
        (~df["steam_price_min"].isna()) & (~df["steam_price_max"].isna()),
        np.round((df["steam_price_min"] + df["steam_price_max"]) / 2, 2),
        np.nan
    )
    
    steam_price_min_ratio = np.mean(df["steam_price"] / df["steam_price_min"])
    steam_price_max_ratio = np.mean(df["steam_price"] / df["steam_price_max"])

    df["steam_price"] = np.where(
        (~df["steam_price_min"].isna()) & (df["steam_price"].isna()),
        np.round(df["steam_price_min"] * steam_price_min_ratio, 2),
        df["steam_price"]
    )

    df["steam_price"] = np.where(
        (~df["steam_price_max"].isna()) & (df["steam_price"].isna()),
        np.round(df["steam_price_max"] * steam_price_max_ratio, 2),
        df["steam_price"]
    )

    df["steam_price"] = np.maximum(df["steam_price"], 0.03)

    df["steam_price_taxed"] = np.where(
        ~df["steam_price"].isna(),
        np.round(df["steam_price"] / 1.15 - 0.0119, 2),
        np.nan
    )

    filtered_df = df[
        (~df["pricereal24h"].isna()) &
        (~df["pricereal7d"].isna()) &
        (~df["pricereal30d"].isna())
    ]

    real_prices_ratios = {
        col: np.mean(filtered_df["pricereal"] / filtered_df[col])
        for col in reversed(["pricereal24h", "pricereal7d", "pricereal30d"])
    }

    real_prices_ratios["pricereal"] = 1

    df["real_price"] = np.nan
    for col, ratio in real_prices_ratios.items():
        mask = (~df[col].isna()) & (df[col] > 0)
        df.loc[mask, "real_price"] = np.round(df.loc[mask, col] * ratio, 2)

    filtered_df = df[~df["steam_price"].isna() & ~df["real_price"].isna()].copy()

    steam_price_to_real_price_ratio = (filtered_df["steam_price"] / filtered_df["real_price"]).mean()
    real_price_to_steam_price_ratio = 1 / steam_price_to_real_price_ratio

    df["estimated_steam_price"] = np.where(
        ~df["real_price"].isna(),
        np.maximum(0.03, np.round(df["real_price"] * steam_price_to_real_price_ratio, 2)),
        np.nan
    )

    df["estimated_steam_price_taxed"] = np.where(
        ~df["estimated_steam_price"].isna(),
        np.round(df["estimated_steam_price"] / 1.15 - 0.0119, 2),
        np.nan
    )

    df["estimated_real_price"] = np.where(
        ~df["steam_price"].isna(),
        np.maximum(0.01, np.round(df["steam_price"] * real_price_to_steam_price_ratio, 2)),
        np.nan
    )

    sold_columns = ["sold24h", "sold7d", "sold30d"]
    for col in sold_columns:
        df[col] = np.where(
            (~df["steam_price"].isna()) & (df[col].isna()),
            0,
            df[col]
        )

    rename_map = {
        "sold24h": "steam_sold_24h", "sold7d": "steam_sold_7d", "sold30d": "steam_sold_30d",
        "markethashname": "name","pricerealchangepercent24h": "real_price_change_percent_24h",
        "pricerealchangepercent7d": "real_price_change_percent_7d",
        "pricerealchangepercent30d": "real_price_change_percent_30d",
    }

    df.rename(columns=rename_map, inplace=True)

    if not return_everything:
        df = df[[
            "name", "steam_price", "steam_price_taxed",
            "estimated_steam_price", "estimated_steam_price_taxed",
            "steam_sold_24h", "steam_sold_7d", "steam_sold_30d",
            "real_price", "estimated_real_price"
        ]]

    if return_type == "dataframe":
        return df
    elif return_type == "dict":
        return df.set_index("name").to_dict(orient="index")