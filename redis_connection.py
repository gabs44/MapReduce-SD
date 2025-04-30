import redis

r = redis.StrictRedis(host='redis-local', port=6379, db=0)