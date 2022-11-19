from typing import List

from pydantic import BaseModel

import es_helpers


class SearchResultPost(BaseModel):
    id: str
    post: str
    username: str
    user_bio: str
    post_likes_count: int
    post_diamond_count: int


async def search_posts(term: str, fields: List[str], pit_id: str, limit: int, offset: int) -> List[SearchResultPost]:
    res = await es_helpers.search(
        term=term, fields=fields, pit=pit_id, limit=limit, offset=offset
    )
    posts = [
        SearchResultPost(
            id=post_data["_source"]["id"],
            post=post_data["_source"]["post"],
            username=post_data["_source"]["username"],
            user_bio=post_data["_source"]["user_bio"],
            post_likes_count=post_data["_source"]["post_likes_count"],
            post_diamond_count=post_data["_source"]["post_diamond_count"],
        )
        for post_data in res.hits.hits
    ]
    return posts
