"""
Redis utility client with common Redis operations.
"""

import redis
import json
from typing import Any, Optional, List, Dict, Union


class RedisClient:
    """Redis client utility class with common operations."""
    
    def __init__(
        self,
        host: str = 'redis-17523.c323.us-east-1-2.ec2.cloud.redislabs.com',
        port: int = 17523,
        username: str = "default",
        password: str = "cr4sNMKKcrsczh8ypTk0bn6BnlyljvOP",
        decode_responses: bool = True,
        **kwargs
    ):
        """Initialize Redis connection."""
        self.client = redis.Redis(
            host=host,
            port=port,
            username=username,
            password=password,
            decode_responses=decode_responses,
            **kwargs
        )
    
    # ==================== Connection Methods ====================
    
    def ping(self) -> bool:
        """Check if Redis server is responding."""
        return self.client.ping()
    
    def close(self):
        """Close the Redis connection."""
        self.client.close()
    
    # ==================== String Operations ====================
    
    def get(self, key: str) -> Optional[str]:
        """Get value for a key."""
        return self.client.get(key)
    
    def set(self, key: str, value: Any, ex: Optional[int] = None, px: Optional[int] = None) -> bool:
        """Set key to hold value. ex=seconds, px=milliseconds for expiration."""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return self.client.set(key, value, ex=ex, px=px)
    
    def set_json(self, key: str, value: Any, ex: Optional[int] = None, px: Optional[int] = None) -> bool:
        """Set key to hold JSON-serialized value."""
        return self.client.set(key, json.dumps(value), ex=ex, px=px)
    
    def get_json(self, key: str) -> Optional[Any]:
        """Get and deserialize JSON value for a key."""
        value = self.client.get(key)
        if value:
            return json.loads(value)
        return None
    
    def delete(self, *keys: str) -> int:
        """Delete one or more keys. Returns number of keys deleted."""
        return self.client.delete(*keys)
    
    def exists(self, *keys: str) -> int:
        """Check if one or more keys exist. Returns number of existing keys."""
        return self.client.exists(*keys)
    
    def expire(self, key: str, time: int) -> bool:
        """Set expiration time in seconds for a key."""
        return self.client.expire(key, time)
    
    def ttl(self, key: str) -> int:
        """Get time to live in seconds for a key. Returns -1 if no expiration, -2 if key doesn't exist."""
        return self.client.ttl(key)
    
    def incr(self, key: str, amount: int = 1) -> int:
        """Increment key value by amount. Returns new value."""
        return self.client.incr(key, amount)
    
    def decr(self, key: str, amount: int = 1) -> int:
        """Decrement key value by amount. Returns new value."""
        return self.client.decr(key, amount)
    
    def mget(self, *keys: str) -> List[Optional[str]]:
        """Get values for multiple keys."""
        return self.client.mget(keys)
    
    def mset(self, mapping: Dict[str, Any]) -> bool:
        """Set multiple keys to their respective values."""
        # Serialize dict/list values to JSON
        serialized = {}
        for k, v in mapping.items():
            if isinstance(v, (dict, list)):
                serialized[k] = json.dumps(v)
            else:
                serialized[k] = v
        return self.client.mset(serialized)
    
    # ==================== List Operations ====================
    
    def lpush(self, key: str, *values: Any) -> int:
        """Push values to the left of a list. Returns new list length."""
        serialized = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in values]
        return self.client.lpush(key, *serialized)
    
    def rpush(self, key: str, *values: Any) -> int:
        """Push values to the right of a list. Returns new list length."""
        serialized = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in values]
        return self.client.rpush(key, *serialized)
    
    def lpop(self, key: str, count: Optional[int] = None) -> Optional[Union[str, List[str]]]:
        """Pop and return leftmost element(s) from list."""
        return self.client.lpop(key, count)
    
    def rpop(self, key: str, count: Optional[int] = None) -> Optional[Union[str, List[str]]]:
        """Pop and return rightmost element(s) from list."""
        return self.client.rpop(key, count)
    
    def lrange(self, key: str, start: int = 0, end: int = -1) -> List[str]:
        """Get a range of elements from a list."""
        return self.client.lrange(key, start, end)
    
    def llen(self, key: str) -> int:
        """Get the length of a list."""
        return self.client.llen(key)
    
    def lindex(self, key: str, index: int) -> Optional[str]:
        """Get element at index in a list."""
        return self.client.lindex(key, index)
    
    # ==================== Hash Operations ====================
    
    def hget(self, key: str, field: str) -> Optional[str]:
        """Get value of a hash field."""
        return self.client.hget(key, field)
    
    def hset(self, key: str, field: str, value: Any) -> int:
        """Set value of a hash field."""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return self.client.hset(key, field, value)
    
    def hgetall(self, key: str) -> Dict[str, str]:
        """Get all fields and values in a hash."""
        return self.client.hgetall(key)
    
    def hmset(self, key: str, mapping: Dict[str, Any]) -> bool:
        """Set multiple hash fields to their values."""
        serialized = {}
        for k, v in mapping.items():
            if isinstance(v, (dict, list)):
                serialized[k] = json.dumps(v)
            else:
                serialized[k] = v
        return self.client.hmset(key, serialized)
    
    def hmget(self, key: str, *fields: str) -> List[Optional[str]]:
        """Get values of multiple hash fields."""
        return self.client.hmget(key, fields)
    
    def hdel(self, key: str, *fields: str) -> int:
        """Delete one or more hash fields. Returns number of fields deleted."""
        return self.client.hdel(key, *fields)
    
    def hexists(self, key: str, field: str) -> bool:
        """Check if a hash field exists."""
        return self.client.hexists(key, field)
    
    def hlen(self, key: str) -> int:
        """Get the number of fields in a hash."""
        return self.client.hlen(key)
    
    def hkeys(self, key: str) -> List[str]:
        """Get all field names in a hash."""
        return self.client.hkeys(key)
    
    def hvals(self, key: str) -> List[str]:
        """Get all values in a hash."""
        return self.client.hvals(key)
    
    def hincrby(self, key: str, field: str, amount: int = 1) -> int:
        """Increment hash field value by amount. Returns new value."""
        return self.client.hincrby(key, field, amount)
    
    # ==================== Set Operations ====================
    
    def sadd(self, key: str, *values: Any) -> int:
        """Add one or more members to a set. Returns number of members added."""
        return self.client.sadd(key, *values)
    
    def smembers(self, key: str) -> set:
        """Get all members of a set."""
        return self.client.smembers(key)
    
    def srem(self, key: str, *values: Any) -> int:
        """Remove one or more members from a set. Returns number of members removed."""
        return self.client.srem(key, *values)
    
    def sismember(self, key: str, value: Any) -> bool:
        """Check if value is a member of a set."""
        return self.client.sismember(key, value)
    
    def scard(self, key: str) -> int:
        """Get the number of members in a set."""
        return self.client.scard(key)
    
    def spop(self, key: str, count: Optional[int] = None) -> Optional[Union[str, set]]:
        """Remove and return one or more random members from a set."""
        return self.client.spop(key, count)
    
    # ==================== Sorted Set Operations ====================
    
    def zadd(self, key: str, mapping: Dict[str, float]) -> int:
        """Add one or more members to a sorted set with scores."""
        return self.client.zadd(key, mapping)
    
    def zrange(self, key: str, start: int = 0, end: int = -1, withscores: bool = False) -> List[Union[str, tuple]]:
        """Get a range of members from a sorted set."""
        return self.client.zrange(key, start, end, withscores=withscores)
    
    def zrem(self, key: str, *members: str) -> int:
        """Remove one or more members from a sorted set."""
        return self.client.zrem(key, *members)
    
    def zscore(self, key: str, member: str) -> Optional[float]:
        """Get the score of a member in a sorted set."""
        return self.client.zscore(key, member)
    
    def zcard(self, key: str) -> int:
        """Get the number of members in a sorted set."""
        return self.client.zcard(key)
    
    def zrank(self, key: str, member: str) -> Optional[int]:
        """Get the rank of a member in a sorted set (0-based, ascending)."""
        return self.client.zrank(key, member)
    
    def zrevrank(self, key: str, member: str) -> Optional[int]:
        """Get the rank of a member in a sorted set (0-based, descending)."""
        return self.client.zrevrank(key, member)
    
    # ==================== General Operations ====================
    
    def keys(self, pattern: str = "*") -> List[str]:
        """Find all keys matching pattern."""
        return self.client.keys(pattern)
    
    def flushdb(self) -> bool:
        """Delete all keys in the current database."""
        return self.client.flushdb()
    
    def flushall(self) -> bool:
        """Delete all keys in all databases."""
        return self.client.flushall()
    
    def type(self, key: str) -> str:
        """Get the type of value stored at key."""
        return self.client.type(key)
    
    def rename(self, key: str, new_key: str) -> bool:
        """Rename a key."""
        return self.client.rename(key, new_key)
    
    def move(self, key: str, db: int) -> bool:
        """Move a key to another database."""
        return self.client.move(key, db)


# Create a default instance for backward compatibility
r = RedisClient()

