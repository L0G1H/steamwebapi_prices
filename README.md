# Steamwebapi Prices

Python module for getting Steam Market and third-party website prices for items from CS2, Dota 2, Rust, and Team Fortress 2.

## Installation

```bash
pip install git+https://github.com/L0G1H/steamwebapi_prices.git
```

## Usage

```python
from steamwebapi_prices import get_prices

# Get CS2 prices in EUR
prices = get_prices("YOUR_API_KEY")

# Get Dota 2 prices in USD
prices = get_prices("YOUR_API_KEY", game="dota2", currency="USD")

# Get as dictionary instead of DataFrame
prices = get_prices("YOUR_API_KEY", return_type="dict")

# Get all available data
prices = get_prices("YOUR_API_KEY", return_everything=True)
```

## Parameters

| Parameter         | Type | Default     | Description                                            |
|-------------------|------|-------------|--------------------------------------------------------|
| api_key           | str  |             | Your API key from steamwebapi.com                      |
| game              | str  | "cs2"       | Game to get prices for ("cs2", "dota2", "rust", "tf2") |
| currency          | str  | "EUR"       | Currency code (EUR, USD, etc.)                         |
| return_type       | str  | "dataframe" | Return type ("dataframe" or "dict")                    |
| return_everything | bool | False       | Return all available data                              |

## Return Data

Default columns:
- name: Item name
- steam_price: Current Steam Market price
- steam_price_taxed: Steam Market price after fees
- estimated_steam_price: Estimated Steam price based on real price
- estimated_steam_price_taxed: Estimated Steam price after fees
- steam_sold_24h: Items sold in last 24h
- steam_sold_7d: Items sold in last 7 days
- steam_sold_30d: Items sold in last 30 days
- real_price: Current third-party website price
- estimated_real_price: Estimated real price based on Steam price

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.