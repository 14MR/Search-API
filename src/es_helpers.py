from typing import Optional, List

import httpx
from pydantic import BaseModel, Field

import config

keep_alive_pit = "10m"


class ESSearchResultHits(BaseModel):
    total: dict
    max_score: float
    hits: List[dict]


class ESSearchResultResponse(BaseModel):
    pit_id: str
    took: int
    timed_out: bool
    shards: dict = Field(alias="_shards")
    hits: ESSearchResultHits


async def get_pit() -> str:
    data = await make_es_request(
        "POST", make_url("_pit", index=config.ES_INDEX), params={"keep_alive": keep_alive_pit}
    )
    return data["id"]


async def make_es_request(
        method: str,
        url: str,
        params: Optional[dict] = dict,
        data: Optional[dict] = None,
        json: Optional[dict] = None,
):
    async with httpx.AsyncClient() as client:
        request = await client.request(
            method=method, url=url, params=params, data=data, json=json
        )
        return request.json()


async def search(term: str, fields: List[str], pit: str, limit: int, offset: int) -> ESSearchResultResponse:
    query = {
        "size": limit,
        "from": offset,
        "pit": {"id": pit, "keep_alive": keep_alive_pit},
        "query": {"query_string": {"query": term, "fields": fields}},
    }

    async with httpx.AsyncClient() as client:
        data = await client.post(make_url("_search", None), json=query)
        return ESSearchResultResponse(**data.json())
    


def make_url(method: str, index: Optional[str]):
    if index:
        return f"{config.ES_URL}{index}/{method}"
    else:
        return f"{config.ES_URL}{method}"
