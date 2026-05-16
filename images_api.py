import requests
from urllib.parse import quote

WIKI_COMMONS = "https://commons.wikimedia.org/w/api.php"

HEADERS = {
    "User-Agent": "petcare-chatbot/1.0 (https://example.com; contact: none)"
}

def fetch_images_online(query: str, limit: int = 4):
    """
    Wikimedia Commons se FREE images (direct URLs)
    """
    query = (query or "").strip()
    if not query:
        return []

    # Step-1: commons me file search
    params1 = {
        "action": "query",
        "list": "search",
        "srsearch": f"{query} filetype:bitmap",   # better for images
        "srnamespace": 6,                         # File:
        "srlimit": limit,
        "format": "json",
        "origin": "*"                             # harmless on server, useful sometimes
    }

    r1 = requests.get(WIKI_COMMONS, params=params1, timeout=20, headers=HEADERS)
    r1.raise_for_status()
    data1 = r1.json()

    results = data1.get("query", {}).get("search", [])
    titles = [x.get("title") for x in results if x.get("title")]
    if not titles:
        return []

    # Step-2: titles se direct image URLs nikaalo
    params2 = {
        "action": "query",
        "titles": "|".join(titles),
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json",
        "origin": "*"
    }

    r2 = requests.get(WIKI_COMMONS, params=params2, timeout=20, headers=HEADERS)
    r2.raise_for_status()
    data2 = r2.json()

    pages = data2.get("query", {}).get("pages", {})
    urls = []
    for _, p in pages.items():
        info = p.get("imageinfo", [])
        if info and info[0].get("url"):
            urls.append(info[0]["url"])

    # unique + limit
    out = []
    seen = set()
    for u in urls:
        if u not in seen:
            out.append(u)
            seen.add(u)
        if len(out) >= limit:
            break

    return out


def fetch_images(query: str, base_url: str = "", limit: int = 4, mode: str = "online"):
    # ab tumhe online hi chahiye, so always online
    return fetch_images_online(query, limit)