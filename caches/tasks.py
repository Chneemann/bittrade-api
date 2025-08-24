from celery import shared_task
from django.core.cache import cache
from django.conf import settings
import requests

COIN_TTL = 24 * 60 * 60  # 24h

@shared_task
def cache_coin_data(coin_id: str):
    """
    Loads a single coin from CoinGecko and saves it in Redis.
    """
    url = f"{settings.COINGECKO_API_URL}/coins/{coin_id.lower()}"

    params = {}
    if settings.COINGECKO_API_KEY:
        params['x_cg_demo_api_key'] = settings.COINGECKO_API_KEY

    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        redis_key = f"coin:{coin_id.lower()}"
        cache.set(redis_key, data, timeout=COIN_TTL)

        return f"{redis_key} cached successfully"

    except requests.RequestException as e:
        return f"Error caching {coin_id}: {str(e)}"