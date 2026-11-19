import httpx


OPENALEX_URL = "https://api.openalex.org/works"


def reconstruct_abstract(inverted_index):
    """
    Convert OpenAlex abstract inverted index into readable text.
    """

    if not inverted_index:
        return ""

    words = {}

    for word, positions in inverted_index.items():
        for position in positions:
            words[position] = word

    return " ".join(
        words[position]
        for position in sorted(words)
    )


async def retrieve_evidence(query):

    params = {
        "search": query,
        "per_page": 5,
        "select": (
            "id,doi,title,publication_year,"
            "abstract_inverted_index,best_oa_location"
        )
    }

    async with httpx.AsyncClient(timeout=30) as client:

        response = await client.get(
            OPENALEX_URL,
            params=params
        )

        response.raise_for_status()

        data = response.json()

    evidence = []

    for paper in data.get("results", []):

        abstract = reconstruct_abstract(
            paper.get("abstract_inverted_index")
        )

        if not abstract:
            continue

        oa_location = paper.get("best_oa_location") or {}

        evidence.append({
            "title": paper.get("title", "Unknown"),
            "source": "OpenAlex",
            "url": paper.get("doi") or oa_location.get("landing_page_url"),
            "evidence_type": "ABSTRACT",
            "text": abstract
        })

    return evidence