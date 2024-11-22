import requests
import pandas as pd
import numpy as np


def get_prices(api_key: str, *, game: str = "cs2", currency: str = "EUR", return_type: str = "dataframe",
               clean_return: bool = True) -> pd.DataFrame | dict:
    """
    Fetch and process item prices from the Steam API.

    :param api_key: Steam API key.
    :param game: Game identifier, e.g., 'cs2', 'dota2', 'rust', 'tf2'.
    :param currency: Currency code, e.g., 'EUR'.
    :param return_type: Return format: 'dataframe' or 'dict'.
    :param clean_return: Whether to return a cleaned-up DataFrame.
    :return: Processed prices as a DataFrame or dictionary.
    """

    allowed_games = {"cs2": "csgo", "dota2": "dota", "rust": "rust", "tf2": "tf2"}
    games_codes = {"cs2": 730, "dota2": 570, "rust": 252490, "tf2": 440}


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
    df = df.infer_objects(copy=False).reset_index()
    df = df.loc[~df.index.duplicated()]
    df.replace(0, np.nan, inplace=True)


    df["game"] = game
    df["game_code"] = games_codes[game]


    filtered_df = df[
        (df["pricereal24h"] > 0) & (df["pricereal7d"] > 0) & (df["pricereal30d"] > 0) & (df["pricereal90d"] > 0)
    ]
    market_shift = {
        col: np.mean(filtered_df["pricereal"] / filtered_df[col])
        for col in ["pricereal24h", "pricereal7d", "pricereal30d", "pricereal90d"]
    }
    market_shift["pricereal"] = 1

    df["real_price"] = np.nan
    for col, ratio in market_shift.items():
        mask = (~df[col].isna()) & (df[col] > 0) & (df["real_price"].isna())
        df.loc[mask, "real_price"] = round(df.loc[mask, col] * ratio, 2)

    df["steam_price_min"] = df[["buyorderprice", "pricemin"]].max(axis=1, skipna=True)
    df["steam_price_max"] = df[["pricemedian", "priceavg", "pricemax"]].min(axis=1, skipna=True)

    df["steam_price"] = np.where(
        (df["steam_price_min"] > 0) & (df["steam_price_max"] > 0),
        round((df["steam_price_min"] + df["steam_price_max"]) / 2, 2),
        np.nan
    )
    df["steam_price_taxed"] = np.where(
        ~pd.isna(df["steam_price"]),
        np.round(df["steam_price"] / 1.15 - 0.0119, 2),
        np.nan
    )

    filtered_df = df[~df["steam_price"].isna() & ~df["real_price"].isna()].copy()
    ratio = (filtered_df["steam_price"] / filtered_df["real_price"]).mean()
    inverse_ratio = 1 / ratio

    df["estimated_steam_price"] = np.where(
        ~df["real_price"].isna(),
        np.maximum(0.03, np.round(df["real_price"] * ratio, 2)),
        np.nan
    )
    df["estimated_steam_price_taxed"] = np.where(
        ~pd.isna(df["estimated_steam_price"]),
        np.maximum(0.01, np.round(df["estimated_steam_price"] / 1.15 - 0.0119, 2)),
        np.nan
    )
    df["estimated_real_price"] = np.where(
        ~df["steam_price"].isna(),
        np.maximum(0.01, np.round(df["steam_price"] * inverse_ratio, 2)),
        np.nan
    )

    sold_columns = ["sold24h", "sold7d", "sold30d", "sold90d"]
    for col in sold_columns:
        df[col] = np.where(
            (~df["steam_price"].isna()) & (df[col].isna()),
            0,
            df[col]
        )

    rename_map = {
        "sold24h": "steam_sold_24h", "sold7d": "steam_sold_7d", "sold30d": "steam_sold_30d", "sold90d": "steam_sold_90d",
        "itemimage": "image", "markethashname": "name",
        "pricerealchangepercent24h": "real_price_change_percent_24h",
        "pricerealchangepercent7d": "real_price_change_percent_7d",
        "pricerealchangepercent30d": "real_price_change_percent_30d",
        "pricerealchangepercent90d": "real_price_change_percent_90d"
    }
    df.rename(columns=rename_map, inplace=True)

    if clean_return:
        df = df[[
            "name", "game", "game_code", "steam_price", "steam_price_taxed",
            "estimated_steam_price", "estimated_steam_price_taxed",
            "steam_sold_24h", "steam_sold_7d", "steam_sold_30d", "steam_sold_90d",
            "real_price", "estimated_real_price",
            "real_price_change_percent_24h", "real_price_change_percent_7d",
            "real_price_change_percent_30d", "real_price_change_percent_90d"
        ]]

    if return_type == "dataframe":
        return df
    elif return_type == "dict":
        return df.set_index("name").to_dict(orient="index")