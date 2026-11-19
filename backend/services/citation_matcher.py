import re

from rapidfuzz import fuzz


def normalize_text(text):

    text = text.lower()

    text = re.sub(
        r'[^a-z0-9 ]',
        ' ',
        text
    )

    text = re.sub(
        r'\s+',
        ' ',
        text
    )

    return text.strip()


def extract_author_year(citation):

    year_match = re.search(
        r'(19|20)\d{2}',
        citation
    )

    year = year_match.group() if year_match else None

    author_match = re.search(
        r'[A-Z][A-Za-z\'-]+',
        citation
    )

    author = (
        author_match.group()
        if author_match
        else None
    )

    return author, year


def match_citations(citations, references):

    results = []

    for citation in citations:

        citation_author, citation_year = (
            extract_author_year(citation)
        )

        best_match = None
        best_score = 0

        for reference in references:

            normalized_citation = normalize_text(
                citation
            )

            normalized_reference = normalize_text(
                reference
            )

            score = fuzz.partial_ratio(
                normalized_citation,
                normalized_reference
            )

            reference_year = (
                citation_year
                in reference
                if citation_year
                else False
            )

            if reference_year:
                score += 15

            if score > best_score:

                best_score = score
                best_match = reference

        results.append({

            "citation": citation,

            "matched_reference": best_match,

            "match_score": min(best_score, 100),

            "status": (
                "MATCHED"
                if best_score >= 65
                else "NEEDS_REVIEW"
            )

        })

    return results