import httpx

from urllib.parse import quote


CROSSREF_URL = "https://api.crossref.org/works"

OPENALEX_URL = "https://api.openalex.org/works"


async def search_crossref(query):

    params = {
        "query.bibliographic": query,
        "rows": 5
    }

    async with httpx.AsyncClient(timeout=20) as client:

        response = await client.get(
            CROSSREF_URL,
            params=params
        )

        response.raise_for_status()

        data = response.json()

    results = []

    for item in data["message"]["items"]:

        authors = []

        for author in item.get("author", []):

            authors.append(
                author.get("given", "")
                + " "
                + author.get("family", "")
            )

        title_list = item.get("title", [])

        title = (
            title_list[0]
            if title_list
            else "Unknown Title"
        )

        results.append({

            "title": title,

            "authors": authors,

            "year": (
                item.get("published", {})
                .get("date-parts", [[None]])[0][0]
            ),

            "doi": item.get("DOI"),

            "journal": (
                item.get("container-title", [""])[0]
            ),

            "source": "Crossref",

            "url": (
                "https://doi.org/"
                + item["DOI"]
                if item.get("DOI")
                else None
            )

        })

    return results


async def search_openalex(query):

    params = {
        "search": query,
        "per_page": 5,
        "select": (
            "id,doi,title,publication_year,"
            "authorships,open_access,primary_location"
        )
    }

    async with httpx.AsyncClient(timeout=20) as client:

        response = await client.get(
            OPENALEX_URL,
            params=params
        )

        response.raise_for_status()

        data = response.json()

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

            "url": item.get("doi")

        })

    return results


async def search_research_papers(query):

    crossref_results = await search_crossref(query)

    openalex_results = await search_openalex(query)

    return {
        "query": query,
        "crossref": crossref_results,
        "openalex": openalex_results
    }