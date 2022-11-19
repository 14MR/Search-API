import asyncio
import aiofiles
from aiocsv import AsyncDictReader
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_streaming_bulk
from src import config

es = AsyncElasticsearch(hosts=[f"{config.ES_URL}{config.ES_INDEX}/"])


async def gendata():
    async with aiofiles.open(
            "posts_data.csv", mode="r", encoding="utf-8", newline=""
    ) as afp:
        async for row in AsyncDictReader(afp):
            yield row  # row is a dict


async def main():
    async for ok, result in async_streaming_bulk(es, gendata()):
        action, result = result.popitem()
        if not ok:
            print("failed to %s document %s" % (action, result))


loop = asyncio.new_event_loop()
loop.run_until_complete(main())
