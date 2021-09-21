import celery
from celery import shared_task
import time
from time import sleep
from nsetools import Nse
from django.core.cache import cache
from .models import *
nse = Nse()

@shared_task
def compute_portfolio_data():
    prices = update_current_prices()
    cache.set('prices', prices, 15)
    return None

def market_open():
	stock = nse.get_quote('infy')
	if stock['closePrice']!=0.0:
		market_status = False
		return False
	else:
		market_status = True
		return True

def current_price(sym):
    if market_open():
        return nse.get_quote(sym)['lastPrice']
    else:
        return nse.get_quote(sym)['closePrice']

def update_current_prices():
    while not cache.get('investments'):
        sleep(0.5)
    investments = cache.get('investments')
    print('retrieved investments from cache')
    investment_list = [ investment.stock.symbol for investment in investments]
    print(f"started pulling price data at {time.strftime('%X')}")
    syms = investment_list
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