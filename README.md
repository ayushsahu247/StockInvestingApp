Stock Investor App - Watch video for demo.
https://www.youtube.com/watch?v=M3HVutuZOig&t=10s
A stock investing app which has following functionalities-
1. View all stocks listed on the National Stock Exchange.
2. View the top gainers and losers of today.
3. Buy/Sell stocks (intraday trading available).
4. Every user starts with a balance of 1 lakh Rs.
5. View all of your orders.
6. A portfolio which shows all your stocks, as well as the amount invested in them and the current value.
7. Simplistic color coding to show which investments have been profitable.

Steps for Installation - 
1. Install Django (v>=3.2)
2. Install nsetools
3. Install Postgresql. After basic configuration, create a db called 'investdb', and a user, and grant all privileges to this user for this db. Do the necessary configs in settings.py DATABASES dictionary.
4. Set up Redis.
5. Install Celery.
6. Install django_celery_results and django_celery_beat.
7. Run > python manage.py migrate
8. Create a superuser > python manage.py createsuperuser  (to access the admin panel). 
9. Now Run > python manage.py runserver
10. Open two more terminals and navigate to investpro (the folder containing manage.py)
11. In one, run > celery -A investpro worker -l info 
12. In the second, run > celery -A investpro beat -l info


Redis Commands : 
1. In settings.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": [
            "redis://127.0.0.1:6379/1",
            "redis://127.0.0.1:6379/2",
        ],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.ShardClient",
        }
    }
}

This sets the caching database to redis, and then we can use the django caching tech to directly use redis.

2. After this, we do not need to use Redis commands, but django commands do the needful.

Storage of data: 
A general framework is - 

cache.set('theKey', theValue, timeout_in_seconds)

Retrieval: 

The general framework is - 
theValue = cache.get('theKey') 

These commands are used as per the situation for storage and access of data.
