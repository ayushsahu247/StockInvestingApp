from django.shortcuts import redirect, render
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
import decimal
import numpy as np
from nsetools import Nse
from django.core.cache import cache
import time


nse=Nse()


market_status = False
def market_open():
	stock = nse.get_quote('infy')
	if stock['closePrice']!=0.0:
		market_status = False
		return False
	else:
		market_status = True
		return True

def current_price(symbol):
	if market_open():
		price = nse.get_quote(symbol)['lastPrice']
	else:
		price = nse.get_quote(symbol)['closePrice']
	return price


# Create your views here.

def top_movers(request):

	if cache.get('top_moversCache'):
		context = cache.get('top_moversCache')
	else:
		print(f"started pulling mover data at {time.strftime('%X')}")
		top_gainers = nse.get_top_gainers()[:5]
		top_losers = nse.get_top_losers()[:5]
		print(f"finished pulling mover data at {time.strftime('%X')}")
		if True:   #Market is close, so use Close Price, else, use lastPrice
			top_gainer_info = [ [stock['symbol'],
				stock['ltp'] ]
				for stock in top_gainers[:5] ]  

			top_loser_info = [[stock['symbol'], 
				stock['ltp'] ]
				for stock in top_losers[:5] ]  
			# top_gainer_info = [['TATASTEEL', 'Tata Steel Limited', 1519.4],
			# 	['BAJFINANCE', 'Bajaj Finance Limited', 6377.15],
			# 	['M&M', 'Mahindra & Mahindra Limited', 799.3],
			# 	['BRITANNIA', 'Britannia Industries Limited', 3655.3],
			# 	['IOC', 'Indian Oil Corporation Limited', 107.2]]

			# top_loser_info = [['TATASTEEL', 'Tata Steel Limited', 1519.4],
			# 	['BAJFINANCE', 'Bajaj Finance Limited', 6377.15],
			# 	['M&M', 'Mahindra & Mahindra Limited', 799.3],
			# 	['BRITANNIA', 'Britannia Industries Limited', 3655.3],
			# 	['IOC', 'Indian Oil Corporation Limited', 107.2]]
		context = {'top_gainers':top_gainer_info, 'top_losers':top_loser_info}
		cache.set('top_moversCache', context, 30)
	return render(request, 'top_movers.html', context)


def home(request):
	print("Home activated")
	if request.user.is_authenticated:
		cache.set('prices', None) 
		investor = Investor.objects.get(user_id=request.user.id)
		investments = Investment.objects.filter(investor=investor)
		print("*****************************")
		print("Uploading investment objects in cache")
		cache.set('investments', investments)
		print(investments)
		print("Investments cached sucessfully.")
		print("*****************************")
	else:
		print("*****************************")
		print("User unauthenticated")
		print("*****************************")
	return render(request, 'home.html')

def register(request):
	if request.method == 'POST':
		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']

		if User.objects.filter(email=email).exists():
			messages.info(request, 'Email already used')
		
		elif User.objects.filter(username=username).exists():
			messages.info(request, 'Username already used')
		
		else:   
			user = User.objects.create_user(username=username, email=email, password=password)
			user.save()
			investor = Investor(user=user)
			investor.save()
			return redirect('login')
	return render(request, 'register.html')


def login(request):
	if request.method=='POST':
		username = request.POST['username']
		password = request.POST['password']

		user = auth.authenticate(username=username, password=password)
		if user is not None:
			auth.login(request, user)
			return redirect('/')
		else:
			messages.info(request, 'Invalid Credentials')

	return render(request, 'login.html')

@login_required(login_url='login')
def logout(request):
	auth.logout(request)
	return render(request, 'home.html')



all_stock_codes = nse.get_stock_codes()

del all_stock_codes['SYMBOL']

@login_required(login_url='login')
def all_stocks(request):
	return render(request, 'all_stocks.html', {'all_stock_codes':all_stock_codes})


@login_required(login_url='login')
def stockinfo(request, symbol):  #this page will have the buy/sell functionality. Not now, but shortly.
	stock = Stock.objects.get(symbol=symbol)
	investor = Investor.objects.get(user_id=request.user.id)
	if Investment.objects.filter(investor=investor, stock=stock).exists():
		investment = Investment.objects.get(investor=investor, stock=stock)
		print('investment exists ', investment)
	else:
		investment = None
		print('investment does not exist')
	if market_open():
		price = nse.get_quote(symbol)['lastPrice']
	else:
		price = nse.get_quote(symbol)['closePrice']
	return render(request, 'stock.html', {'stock':stock, 'price':price, 'investment':investment})

@login_required(login_url='login')
def buy(request, symbol):
	stock = Stock.objects.get(symbol=symbol)
	investor = Investor
	if market_open():
		currentPrice = nse.get_quote(symbol)['lastPrice']
			
	else:
		currentPrice = nse.get_quote(symbol)['closePrice']
	if request.method=='POST':
		n_buy = int(float(request.POST['shares']))
		
		expense = n_buy * currentPrice

		#get user's investor profile
		investor = Investor.objects.get(user_id=request.user.id)
		balance = float(investor.balance)

		#conditions
		if expense > balance:
			messages.info(request, 'Not enough balance.')
			return render(request, 'err_insufficient_balance.html', {'balance':balance, 'expense':expense})


		else:
			investor.balance -= decimal.Decimal(expense)
			
			#if  user is already invested then update existing information
			if Investment.objects.filter(investor=investor, stock=stock).exists():   
				investment = Investment.objects.get(investor=investor, stock=stock)
				investment.avg_price = (float(investment.n_shares*investment.avg_price)  +  float(n_buy*currentPrice))/(investment.n_shares+n_buy)
				investment.n_shares+=n_buy
				order_message = Record(investor=investor, stock=stock, message= str('Buy order executed for {} shares of {} at price {}'.format(n_buy, stock.companyName, currentPrice)) )

			else: # Make an investment object for this user and stock
				investment = Investment(investor=investor, stock=stock,n_shares=0,avg_price=0)
				investment.avg_price = (investment.n_shares*investment.avg_price  +  n_buy*currentPrice)/(investment.n_shares+n_buy)
				investment.n_shares+=n_buy
				
				order_message = Record(investor=investor, stock=stock, message= str('Buy order executed for {} shares of {} at price {}'.format(n_buy, stock.companyName, currentPrice)) )
				
			investment.save()
			investor.save()
			order_message.save()
			investment = Investment.objects.get(investor = investor, stock=stock)
			investments = Investment.objects.filter(investor=investor)
			cache.set('investments', investments)
			try:
				prices = cache.get('prices')
				prices['{investment.stock.symbol}':currentPrice]
				cache.set('prices', prices)
				print(prices)
			except:
				print('This buy could not be cached')
		return redirect('/notifications')
	
	return render(request, 'buy.html', {'stock':stock, 'price':currentPrice})
@login_required(login_url='login')
def sell(request, symbol):
	stock = Stock.objects.get(symbol=symbol)
	if request.method=='POST':
		n_sell = int(request.POST['shares'])

		#get the investor
		investor = Investor.objects.get(user_id=request.user.id)

		#check if investment exists
		if Investment.objects.filter(investor=investor, stock=stock).exists(): 
			#if yes, get it
			investment = Investment.objects.get(investor=investor, stock=stock)

			if int(investment.n_shares) < int(n_sell):
				messages.info(request, 'You cannot sell more shares than you possess.')
				return render(request, 'err_insufficient_shares.html', {'shares_owned':investment.n_shares, 'n_sell':n_sell, 'stock':investment.stock.symbol})
			else:
				if market_open():
					currentPrice = nse.get_quote(symbol)['lastPrice']	
				else:
					currentPrice = nse.get_quote(symbol)['closePrice']
				
				income = int(n_sell) * currentPrice
				if investment.n_shares - n_sell == 0:
					investment.avg_price = 0
				else:	
					investment.avg_price = (investment.n_shares*investment.avg_price -  decimal.Decimal(n_sell*currentPrice))/(investment.n_shares - n_sell)
				investment.n_shares-=int(n_sell)
				investor.balance += decimal.Decimal(income)
				investment.save()
				investor.save()
				if investment.n_shares==0:
					investment.delete()
				order_message = Record(investor=investor, stock=stock, message= str('Sell order executed for {} shares of {} at price {}'.format(n_sell, stock.companyName, currentPrice)) )
				order_message.save()
			return redirect('/portfolio')
		else:
			messages.info(request, 'You do not own these stocks.')
	
	return render(request, 'sell.html', {'stock':stock})
		


def portfolio_stocks_data(investments):
	if market_open():
		if cache.get('prices'):
			prices = cache.get('prices')
			print(prices)
			stocks = { investment : np.around(
				list(np.array([float(prices[investment.stock.symbol]) ]*2)*np.array([1, float(investment.n_shares)]))
				+[float(investment.avg_price)*float(investment.n_shares)],
				2) 
				for investment in investments}
		else:
			stocks = { investment : np.around(
				list(np.array([float(0) ]*2)*np.array([1, float(investment.n_shares)]))
				+[float(investment.avg_price)*float(investment.n_shares)],
				2) 
				for investment in investments}
		#this dictionary then has
		# the stock object as its key and the current price as its value.
	else:
		if cache.get('prices'):
			prices = cache.get('prices')
			stocks = { investment : np.around(
				list(np.array([float(prices[investment.stock.symbol]) ]*2)*np.array([1, float(investment.n_shares)]))
				+[float(investment.avg_price)*float(investment.n_shares)],
				2) 
				for investment in investments}
		else:
			stocks = { investment : np.around(
				list(np.array([float(0) ]*2)*np.array([1, float(investment.n_shares)]))
				+[float(investment.avg_price)*float(investment.n_shares)],
				2) 
				for investment in investments}
		# storing in 0th index the closePrice (current price) and in the 1st index currentPrice*n_shares
		# in the 2nd index avg_price * n_shares
		# The dictionary stocks then looks like
		# {investment_object : [currentPrice, currentValue, investedValue]}

	return stocks

def portfolio_computation(request, investments, stocks, user_id):
	print(f"started invested_value at {time.strftime('%X')}")
	invested_value = round(sum([ investment.avg_price*investment.n_shares for investment in investments]), 2)  #input is investments
	print(f"started current_value at {time.strftime('%X')}")
	if cache.get('prices'):
		prices = cache.get('prices')
		current_value = round((sum([(prices[investment.stock.symbol]*investment.n_shares) for investment in investments])), 2)
	else:
		current_value = 0	
		# current_value = round((sum([(current_price(investment.stock.symbol)*investment.n_shares) for investment in investments])), 2)  #input investments
	print(f"started context at {time.strftime('%X')}")
	context = {'investments':stocks, 'investor':Investor.objects.get(user_id=user_id), 'invested_value':invested_value, 'current_value':current_value}
	print(f"finished context at {time.strftime('%X')}")

	return (context)

@login_required(login_url='login')
def portfolio(request):

	context = {}
	if cache.get('portfolioCache'):
		context = cache.get('portfolioCache')
	else:
		user_id = request.user.id
		investments = Investment.objects.filter(investor_id = user_id)
		print(f"started pulling portfolio data at {time.strftime('%X')}")
		stocks = portfolio_stocks_data(investments=investments)
		print(f"finished pulling portfolio data at {time.strftime('%X')}")


		context = portfolio_computation(request, investments=investments, stocks = stocks, user_id = user_id)
		
		cache.set('portfolioCache', context, 5)
		print(f"done with computations at {time.strftime('%X')}")
	return render(request, 'portfolio.html', context) 
	# then, stocks has investment object as the key, and currentPrice as the value
	# so, company name can be accessed (in jinja) as investments.stock.companyName
	# investment.n_shares, investment.avg_price
	# call it as: for investment, stockPrice in investments.items
@login_required(login_url='login')
def notifications(request):
	pass
	records = Record.objects.filter(investor_id=request.user.id)
	return render(request, 'notifications.html', {'records':records[::-1]})

@login_required(login_url='login')
def profile(request):
	investor = Investor.objects.get(user_id=request.user.id)
	return render(request, 'profile.html', {'investor':investor})

