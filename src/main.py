from typing import List

from fastapi import FastAPI
from fastapi import Query, Request, Response
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
import posts
import es_helpers
import config

limiter = Limiter(key_func=get_remote_address, storage_uri=config.REDIS_URL)

app = FastAPI(
    title="Search API"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


class SearchResultResponse(BaseModel):
    pit_id: str
    posts: List[posts.SearchResultPost]


@app.get("/search/", response_model=SearchResultResponse, tags=['search'])
@limiter.limit("100/minute;10000/day")
async def search(
        request: Request,  # required for rate limiter
        response: Response,  # required for rate limiter
        q: str = Query(description="Keyword to search for"),
        fields: list[str] | None = Query(
            default=None,
            description="columns to search in. Eg. `post`, `user_bio`, `username`"
        ),
        pit_id: str
                | None = Query(
            default=None,
            description="Point in time parameter in order to get consistent results",
        ),
        limit: int = Query(default=20, description="limit results"),
        offset: int = Query(default=0, description="offset results"),
):
    if not pit_id:  # if PIT is not provided, request new one
        pit_id = await es_helpers.get_pit()
    post_results = await posts.search_posts(term=q, fields=fields, pit_id=pit_id, limit=limit, offset=offset)
    resp = SearchResultResponse(pit_id=pit_id, posts=post_results)
    return resp
