"""Basic connection example.
"""

import redis

r = redis.Redis(
    host='redis-17523.c323.us-east-1-2.ec2.cloud.redislabs.com',
    port=17523,
    decode_responses=True,
    username="default",
    password="cr4sNMKKcrsczh8ypTk0bn6BnlyljvOP",
)

success = r.set('foo', 'bar')
# True

result = r.get('foo')
print(result)
# >>> bar

