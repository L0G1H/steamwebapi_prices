import unittest
import pandas as pd
from unittest.mock import patch, Mock
from steam_prices.steam_prices import get_prices


class TestGetPrices(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.mock_response_data = [
            {
                "markethashname": "Item1",
                "buyorderprice": 1.0,
                "pricemin": 1.5,
                "pricemedian": 2.0,
                "priceavg": 2.2,
                "pricemax": 2.5,
                "pricereal": 1.8,
                "pricereal24h": 1.7,
                "pricereal7d": 1.9,
                "pricereal30d": 2.0,
                "sold24h": 100,
                "sold7d": 500,
                "sold30d": 1500
            }
        ]

    @patch("requests.get")
    def test_successful_api_call(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = self.mock_response_data
        mock_get.return_value = mock_response

        result = get_prices(self.api_key)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue("steam_price" in result.columns)
        self.assertTrue("real_price" in result.columns)

    def test_invalid_game(self):
        with self.assertRaises(ValueError):
            get_prices(self.api_key, game="invalid_game")

    def test_invalid_return_type(self):
        with self.assertRaises(ValueError):
            get_prices(self.api_key, return_type="invalid_type")

    @patch("requests.get")
    def test_dict_return_type(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = self.mock_response_data
        mock_get.return_value = mock_response

        result = get_prices(self.api_key, return_type="dict")
        self.assertIsInstance(result, dict)

    @patch("requests.get")
    def test_return_everything(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = self.mock_response_data
        mock_get.return_value = mock_response

        result = get_prices(self.api_key, return_everything=True)
        self.assertGreater(len(result.columns), 10)

if __name__ == "__main__":
    unittest.main()