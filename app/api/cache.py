import redis
import pickle

rds = redis.Redis('localhost')
redis = redis.Redis('localhost')
expire = 86400 # seconds

def get_url_cache(cached):
    return pickle.loads(cached)

def set_url_cache(path, payload):
    redis.setex(path, pickle.dumps(payload), 90)
