import httpx
import asyncio
from functools import lru_cache

CROSSREF_URL = "https://api.crossref.org/works"
OPENALEX_URL = "https://api.openalex.org/works"

HEADERS = {
    "User-Agent": "CiteVerify/1.0 (mailto:your-email@example.com)"
}

# Cache search results
cache = {}


async def fetch_with_retry(client, url, params):

    for attempt in range(3):

        try:
            response = await client.get(
                url,
                params=params,
                headers=HEADERS
            )

            if response.status_code == 429:

                await asyncio.sleep(2 ** (attempt + 1))
                continue

            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as error:

            if error.response.status_code == 429:
                continue

            print("API error:", error)
            return None

        except httpx.RequestError as error:

            print("Connection error:", error)

            if attempt < 2:
                await asyncio.sleep(2 ** attempt)

    return None


async def search_crossref(query, client):

    params = {
        "query.bibliographic": query,
        "rows": 5
    }

    data = await fetch_with_retry(
        client,
        CROSSREF_URL,
        params
    )

    if not data:
        return []

    results = []

    for item in data.get("message", {}).get("items", []):

        authors = []

        for author in item.get("author", []):

            authors.append(
                (
                    author.get("given", "") + " "
                    + author.get("family", "")
                ).strip()
            )

        title_list = item.get("title", [])

        doi = item.get("DOI")

        results.append({

            "title": title_list[0] if title_list else "Unknown Title",

            "authors": authors,

            "year": (
                item.get("published", {})
                .get("date-parts", [[None]])[0][0]
            ),

            "doi": doi,

            "journal": (
                item.get("container-title", [""])[0]
            ),

            "source": "Crossref",

            "url": (
                "https://doi.org/" + doi
                if doi else None
            )

        })

    return results


async def search_openalex(query, client):

    params = {
        "search": query,
        "per_page": 5,
        "select": (
            "id,doi,title,publication_year,"
            "authorships,open_access,primary_location"
        )
    }

    data = await fetch_with_retry(
        client,
        OPENALEX_URL,
        params
    )

    if not data:
        return []

    results = []

    for item in data.get("results", []):

        authors = []

        for authorship in item.get("authorships", []):

            author = authorship.get("author", {})

            authors.append(
                author.get("display_name", "")
            )

        results.append({

            "title": item.get("title"),

            "authors": authors,

            "year": item.get("publication_year"),

            "doi": item.get("doi"),

            "source": "OpenAlex",

            "open_access": item.get(
                "open_access", {}
            ).get("is_oa", False),

            "url": (
                item.get("doi")
                or item.get("primary_location", {})
                .get("landing_page_url")
            )

        })

    return results


async def search_research_papers(query):

    query = query.strip()

    if not query:
        return {
            "query": query,
            "crossref": [],
            "openalex": []
        }

    # Return cached results
    if query.lower() in cache:
        return cache[query.lower()]

    async with httpx.AsyncClient(timeout=20) as client:

        crossref_task = search_crossref(query, client)

        openalex_task = search_openalex(query, client)

        crossref_results, openalex_results = await asyncio.gather(
            crossref_task,
            openalex_task
        )

    results = {
        "query": query,
        "crossref": crossref_results,
        "openalex": openalex_results
    }

    cache[query.lower()] = results

    return results