import steam_prices
import os


api_key = os.getenv("steam_web_api")
prices = steam_prices.get_prices(api_key, game="cs2", currency="EUR", return_type="dataframe", clean_return=True)

prices.to_csv("prices.csv", index=False)

# print(prices)

print("Done")

