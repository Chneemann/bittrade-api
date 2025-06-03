import os, json
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db.utils import OperationalError

class CoinsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coins'
    
    def ready(self):
        from coins.models import Coin

        def import_coins(sender, **kwargs):
            try:
                if Coin.objects.exists():
                    return 
                
                path = os.path.join(os.path.dirname(__file__), 'initial_coins.json')
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        coins = json.load(f)
                        for c in coins:
                            Coin.objects.update_or_create(
                                symbol=c['symbol'],
                                defaults={
                                    'name': c['name'],
                                    'slug': c['slug'],
                                }
                            )
            except OperationalError:
                pass

        post_migrate.connect(import_coins, sender=self)