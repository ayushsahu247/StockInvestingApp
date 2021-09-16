from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('top-movers', views.top_movers, name='top-movers'),
    path('register', views.register, name= 'register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('all-stocks', views.all_stocks, name='all-stocks'),
    path('stocks/<str:symbol>/buy', views.buy, name='buy'),
    path('stocks/<str:symbol>/sell', views.sell, name='sell'),
    path('stocks/<str:symbol>/', views.stockinfo, name='stockinfo'),
    path('portfolio', views.portfolio, name='portfolio'),
    path('notifications', views.notifications, name='notifications'),
    path('profile', views.profile, name='profile'),

]