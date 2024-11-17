# Steam Prices

---

A Python library providing pricing for Counter-Strike 2, Dota 2, Rust, and Team Fortress 2 items using the [steamwebapi](https://www.steamwebapi.com/) API. This library calculates and estimates various price values for in-game items, including real prices, Steam prices (with and without taxes), and price changes over different time periods.

### Installation

---

```bash
pip install git+https://github.com/L0G1H/steam_prices.git
```

### Dependencies

---

This library requires the following dependencies, which will be installed automatically:

- `requests`: For making HTTP requests to fetch item data from the Steam API.
- `pandas`: For handling and processing the data in tabular form.
- `numpy`: For numerical operations, especially in price calculations.

### Parameters

---

- `api_key` (str): Your [steamwebapi](https://www.steamwebapi.com/) API key.
- `game` (str, optional): The game from which to fetch item prices. Allowed values: `cs2` (Counter-Strike 2), `dota2`, `rust`, `tf2`. (default is `cs2`).
- `currency` (str, optional): The currency for the prices. Default is `EUR`. (e.g., `USD`, `GBP`).
- `return_type` (str, optional): The format of the returned data. Allowed values: `dataframe`, `dict`. Default is `dataframe`.

### Example

---

```python
import steam_prices

api_key = "your_api_key"

prices = steam_prices.get_prices(api_key, game="cs2", currency="USD", return_type="dict")
```
