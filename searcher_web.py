import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import wikipedia

def wiki_search(query: str, lang="en", sentences=4):
    try:
        wikipedia.set_lang(lang)
        return wikipedia.summary(query, sentences=sentences)
    except Exception:
        return ""

def ddg_search_snippets(query: str, max_results=5):
    snippets = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                if r.get("body"):
                    snippets.append(f"- {r['body']}")
    except Exception:
        pass
    return snippets

def web_context(query: str):
    wiki = wiki_search(query, lang="en", sentences=4)
    ddg = ddg_search_snippets(query, max_results=5)

    parts = []
    if wiki:
        parts.append("WIKIPEDIA SUMMARY:\n" + wiki)

    if ddg:
        parts.append("WEB SNIPPETS:\n" + "\n".join(ddg))

    return "\n\n".join(parts).strip()