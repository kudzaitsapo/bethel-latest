import redis
import pickle

rds = redis.Redis('localhost')
redis = redis.Redis('localhost')
expire = 86400 # seconds

def get_url_cache(cached_payload):
    return pickle.loads(cached_payload)

def set_url_cache(path, payload):
    redis.setex(path, pickle.dumps(payload), 90)

def get_model_cache(cached_model):
    return pickle.loads(cached_model)

def set_model_cache(name, id, model):
    redis.hset(name, id, pickle.dumps(model))
