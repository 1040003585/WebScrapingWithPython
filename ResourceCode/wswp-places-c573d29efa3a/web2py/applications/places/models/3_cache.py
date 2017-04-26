import time

# how often to reset country data
RESET_DB_SECS = 60 * 60
# block malicious crawlers that access banned path
BAN_IP_SECS = 60
# block users who ignore crawl-delay and download too fast
REQUEST_WINDOW = 1
MAX_REQUESTS = 10
# check whether app is being run locally
LOCAL = 'localhost' in request.env.http_host or '127.0.0.1' in request.env.http_host


def ban_client():
    """Temporarily block this client
    """
    ban_key = request.client + 'ban'
    cache.ram(ban_key, None)
    cache.ram(ban_key, lambda: True, BAN_IP_SECS)


if not LOCAL:
    # only block IP's when deployed
    if cache.ram(request.client + 'ban', lambda: False, BAN_IP_SECS):
        # client is blocked
        raise HTTP(429, 'IP temporarily blocked')

    cache.ram(request.client + 'requests', lambda: 0, REQUEST_WINDOW)
    if cache.ram.increment(request.client + 'requests') > MAX_REQUESTS:
        ban_client()


    current_time = time.time()
    cache_time = cache.ram('resetdb', lambda: current_time)
    if current_time > cache_time + RESET_DB_SECS:
        response.flash = response.session = 'test'
        cache.ram.clear('resetdb')
        common = local_import('common', reload=False)
        places = common.Places(db)
        places.load()
