import celery
from celery import shared_task
import time
from time import sleep
from nsetools import Nse
from django.core.cache import cache
nse = Nse()

@shared_task
def compute_portfolio_data():
    prices = update_current_prices()
    cache.set('prices', prices, 9000)
    return None


def current_price(sym):
    return nse.get_quote(sym)['closePrice']

def update_current_prices():
    print(f"started pulling price data at {time.strftime('%X')}")
    syms = list(nse.get_stock_codes().keys())[1:425]
    prices = {}
    for i in range (len(syms)):
        try:
            print(i)
            sym = syms[i]
            print(sym)
            prices[sym] = current_price(sym)
        except:
            print('Some issue with {}'.format(sym, i))
    print(f"finished pulling price data at {time.strftime('%X')}")
    return prices