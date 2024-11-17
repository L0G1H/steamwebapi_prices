import steam_prices
import os


api_key = os.getenv("steam_web_api")
prices = steam_prices.get_prices(api_key, game="cs2", currency="EUR", return_type="dict")

print(prices)