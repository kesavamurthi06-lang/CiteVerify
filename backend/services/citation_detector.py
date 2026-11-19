import re


def extract_dois(text):

    pattern = r'\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b'

    dois = re.findall(
        pattern,
        text,
        flags=re.IGNORECASE
    )

    return list(set(dois))


def extract_in_text_citations(text):

    citations = []

    patterns = [
        # APA / Harvard
        r'\([A-Z][A-Za-z\'-]+(?:\s+et\s+al\.)?,?\s*(?:19|20)\d{2}[a-z]?\)',

        # IEEE
        r'\[(?:\d+(?:\s*[-,]\s*\d+)*)\]',

        # Narrative author-date
        r'\b[A-Z][A-Za-z\'-]+\s+et\s+al\.\s*\((?:19|20)\d{2}[a-z]?\)'
    ]

    for pattern in patterns:

        matches = re.findall(pattern, text)

        citations.extend(matches)

    return list(dict.fromkeys(citations))


def extract_reference_section(text):

    headings = [
        "References",
        "Bibliography",
        "Works Cited",
        "Literature Cited"
    ]

    for heading in headings:

        match = re.search(
            rf'(?im)^\s*{re.escape(heading)}\s*$',
            text
        )

        if match:

            reference_text = text[match.end():]

            return reference_text.strip()

    return ""


def extract_reference_entries(reference_text):

    if not reference_text:
        return []

    lines = reference_text.splitlines()

    references = []

    current_reference = ""

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Detect numbered or author-date reference starts
        is_new_reference = bool(
            re.match(
                r'^(?:\[\d+\]|\d+\.)\s+',
                line
            )
            or re.match(
                r'^[A-Z][A-Za-z\'-]+,?\s+.{0,100}(?:19|20)\d{2}[a-z]?\.',
                line
            )
        )

        if is_new_reference and current_reference:

            references.append(
                current_reference.strip()
            )

            current_reference = line

        else:

            current_reference += " " + line

    if current_reference:
        references.append(current_reference.strip())

    return references


def detect_citations(text):

    in_text = extract_in_text_citations(text)

    reference_section = extract_reference_section(text)

    references = extract_reference_entries(
        reference_section
    )

    dois = extract_dois(reference_section)

    return {
        "in_text_citations": in_text,
        "reference_count": len(references),
        "references": references,
        "dois": dois
    }