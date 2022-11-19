# Search API

Tiny Search API service build on top of Fast API allowing to query data from Elastisearch with a rate-limiter

## Quick start

Simply start the app via docker compose:

```bash
docker-compose up
```

to import the data, you have to install dependencies locally:

```bash
poetry install
python3 import.py
```

## Design

In this section, I will outline thoughts and design decisions which were taken during implementation

### Elasticsearch

#### Field types

I started with designing mapping, looking at the data I identified:`

1. `id`, `username` - these fields are unique identifiers, so they are likely to be selected by exact queries, do not
   have stemming requirements
2. `post`, `user_bio` - these fields are text fields, so we need full-text search features such as stemming, stop words
   filtering
3. `post_like_count`, `post_diamond_count` - integer values, so we can have range queries for them

#### Analysers

I decided to proceed with `standard` tokenizer, it's recommended one and demonstrated good results, comparing to default
settings of other tokenizers.

Filters included:

* `stop` - removes stop words, by default uses English dictionary
* `lowercase` - sets all characters to be lowercase, as register doesn't matter for search
* `porter_stem` - English language stemmer

```json
{
  "mappings": {
    "properties": {
      "id": {
        "type": "keyword"
      },
      "post": {
        "type": "text"
      },
      "username": {
        "type": "keyword"
      },
      "user_bio": {
        "type": "text"
      },
      "post_like_count": {
        "type": "integer"
      },
      "post_diamond_count": {
        "type": "integer"
      }
    }
  },
  "settings": {
    "analysis": {
      "analyzer": {
        "my_analyzer": {
          "tokenizer": "standard",
          "filter": [
            "stop",
            "lowercase",
            "porter_stem"
          ]
        }
      }
    }
  }
}
```

#### What does this mapping support

* [x] Stemming in English
* [x] Multicolumn search
* [x] Index optimizations (do not stem `id`/`username`)
* [ ] Typo support (couldn't make it work with multicolumn queries)

### Python

I have chosen FastAPI as a modern framework with async support, Swagger generation and etc.

#### Elasticsearch adapter

Sadly, popular Elasticsearch libraries did not support all required features (async, PIT, scroll), so I decided to
write `src/es_helper.py` for this to save a bit of time.

#### Point in time API

In order to provide consistent view for API client while paginating, I decided to utilize Point in time API usage, which
allows a client to scroll data in a state they were at the moment client initialized first connection, even if they were
updated. It is implemented as a query parameter, and return after each request

#### Pydantic

In order not to have json/dict hell, all data passed within the project, are wrapped into Pydantic models, including
ElasticSearch responses.

#### Dockerfile

Dockerfile utilizes multistage build with caching support, so final image is slimmer and recurrent builds are faster

#### Rate limiting

Rate limiting is implemented by `slowapi` library, which is based on a popular Flask implementation. It uses Redis
backend in order to allow to scale python containers without loosing global rate-limiting.

#### Documentation

Swagger is available at `http://localhost:8000/docs`
