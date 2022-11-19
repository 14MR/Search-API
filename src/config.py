import os

ES_URL = os.environ.get('ES_URL', 'http://localhost:9200/')
ES_INDEX = os.environ.get('ES_INDEX', 'posts')
REDIS_URL = os.environ.get("REDIS_URL")
