from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock
from django.core.cache import cache
from caches.tasks import cache_coin_data, cache_coin_chart
from requests.exceptions import RequestException

@override_settings(COINGECKO_API_URL="https://api.coingecko.com/api/v3", COINGECKO_API_KEY="test-key")
class CacheCoinTasksTests(TestCase):
    def setUp(self):
        """
        Clear cache before each test.
        """
        cache.clear()

    @patch("caches.tasks.requests.get")
    def test_cache_coin_data_success(self, mock_get):
        """
        Test that coin data is fetched and cached successfully.
        """
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"id": "bitcoin", "symbol": "btc"}
        mock_get.return_value = mock_resp

        result = cache_coin_data("bitcoin")

        redis_key = "coin:bitcoin"
        self.assertEqual(result, f"{redis_key} cached successfully")
        self.assertEqual(cache.get(redis_key), {"id": "bitcoin", "symbol": "btc"})
        mock_get.assert_called_once_with(
            "https://api.coingecko.com/api/v3/coins/bitcoin",
            params={"x_cg_demo_api_key": "test-key"}
        )

    @patch("caches.tasks.requests.get", side_effect=RequestException("API error"))
    def test_cache_coin_data_failure(self, mock_get):
        """
        Test that an API error is handled properly and nothing is cached.
        """
        result = cache_coin_data("bitcoin")
        self.assertIn("Error caching bitcoin", result)
        self.assertIsNone(cache.get("coin:bitcoin"))

    @patch("caches.tasks.requests.get")
    def test_cache_coin_chart_success(self, mock_get):
        """
        Test that historical coin chart data is fetched and cached successfully.
        """
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"prices": [[1234567890, 20000]]}
        mock_get.return_value = mock_resp

        result = cache_coin_chart("bitcoin", "30")

        redis_key = "chart:bitcoin:30"
        self.assertEqual(result, f"{redis_key} cached successfully")
        self.assertEqual(cache.get(redis_key), {"prices": [[1234567890, 20000]]})
        mock_get.assert_called_once_with(
            "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart",
            params={"vs_currency": "usd", "days": "30", "x_cg_demo_api_key": "test-key"}
        )

    @patch("caches.tasks.requests.get", side_effect=RequestException("API error"))
    def test_cache_coin_chart_failure(self, mock_get):
        """
        Test that an API error during chart fetch is handled and cache remains empty.
        """
        result = cache_coin_chart("bitcoin", "30")
        self.assertIn("Error caching bitcoin chart 30d", result)
        self.assertIsNone(cache.get("chart:bitcoin:30"))