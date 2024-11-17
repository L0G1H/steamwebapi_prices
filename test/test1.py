import steam_prices
import os


api_key = "BLCYCV7E0PLL3Q57" # os.getenv("steam_web_api"),
prices = steam_prices.get_prices(api_key, game="cs2", currency="EUR", return_type="dict")

print(prices)