import os
import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
from steamwebapi_prices import get_prices


class TestGetPrices(unittest.TestCase):
    def setUp(self):
        self.api_key = os.getenv("steam_web_api")
        self.mock_items_data = {
            "items": ["Item 1", "Item 2", "Item 3"]
        }
        self.mock_api_response = [
            {
                "markethashname": "Item 1",
                "buyorderprice": 1.0,
                "pricemin": 1.5,
                "pricemedian": 2.0,
                "priceavg": 2.2,
                "pricemax": 3.0,
                "pricereal": 1.8,
                "pricereal24h": 1.7,
                "pricereal7d": 1.9,
                "pricereal30d": 1.6,
                "sold24h": 10,
                "sold7d": 50,
                "sold30d": 150
            }
        ]

    @patch('requests.get')
    def test_valid_input(self, mock_get):
        # Mock API responses
        mock_responses = [
            MagicMock(json=lambda: self.mock_items_data),
            MagicMock(json=lambda: self.mock_api_response)
        ]
        mock_get.side_effect = mock_responses

        result = get_prices(self.api_key)
        self.assertIsInstance(result, pd.DataFrame)

    def test_invalid_game(self):
        with self.assertRaises(ValueError):
            get_prices(self.api_key, game="invalid_game")

    def test_invalid_return_type(self):
        with self.assertRaises(ValueError):
            get_prices(self.api_key, return_type="invalid_type")

    def test_empty_api_key(self):
        with self.assertRaises(ValueError):
            get_prices("")

    @patch('requests.get')
    def test_return_dict(self, mock_get):
        # Mock API responses
        mock_responses = [
            MagicMock(json=lambda: self.mock_items_data),
            MagicMock(json=lambda: self.mock_api_response)
        ]
        mock_get.side_effect = mock_responses

        result = get_prices(self.api_key, return_type="dict")
        self.assertIsInstance(result, dict)

    @patch('requests.get')
    def test_minimum_prices(self, mock_get):
        # Mock API responses with very low prices
        low_price_response = [
            {
                "markethashname": "Item 1",
                "buyorderprice": 0.01,
                "pricemin": 0.01,
                "pricemedian": 0.01,
                "priceavg": 0.01,
                "pricemax": 0.01,
                "pricereal": 0.005,
                "pricereal24h": 0.005,
                "pricereal7d": 0.005,
                "pricereal30d": 0.005,
                "sold24h": 10,
                "sold7d": 50,
                "sold30d": 150
            }
        ]
        mock_responses = [
            MagicMock(json=lambda: self.mock_items_data),
            MagicMock(json=lambda: low_price_response)
        ]
        mock_get.side_effect = mock_responses

        result = get_prices(self.api_key)
        self.assertGreaterEqual(result['steam_price'].min(),
                                0.03)  # MINIMUM_STEAM_PRICE
        self.assertGreaterEqual(result['real_price'].min(), 0.01)  # MINIMUM_REAL_PRICE

    @patch('requests.get')
    def test_api_error(self, mock_get):
        mock_get.side_effect = Exception("API Error")
        with self.assertRaises(SystemExit):
            get_prices(self.api_key)


if __name__ == '__main__':
    unittest.main()