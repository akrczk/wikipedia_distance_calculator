import re
import requests

URL = "https://pl.wikipedia.org/w/api.php"

def get_article_content_and_links(title):
    """Pobiera treść artykułu i linki z API Wikipedii."""

    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts|links",
        "titles": title,
        "explaintext": True,
        "pllimit": "max"
    }
    response = requests.get(URL, params=params)
    data = response.json()

    return {"content": extract_content(data), "links": extract_links(title, data)}

def get_paginated_links(title, continue_str):
    """Rekursywnie otrzymuje linki, kiedy jest ich więcej niż 500."""

    params = {
        "action": "query",
        "format": "json",
        "prop": "links",
        "titles": title,
        "explaintext": True,
        "pllimit": "max",
        "plcontinue": continue_str
    }
    response = requests.get(URL, params=params)
    data = response.json()

    return extract_links(title, data)

def extract_content(data):
    """Otrzymuje zawartość z odpowiedzi API."""
    if not data or "query" not in data or "pages" not in data["query"]:
        return ""
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))

    return page.get("extract", "")

def extract_links(title, data):
    """Otrzymuje linki z odpowiedzi API."""
    if not data or "query" not in data or "pages" not in data["query"]:
        return []
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    links = page.get("links", [])
    links = [link["title"] for link in links]
    if "continue" in data:
        links = links + get_paginated_links(title, data["continue"]["plcontinue"])

    return links

def contains_words(content, word):
    """Sprawdza, czy dane hasło występuje w treści."""

    return bool(re.search(rf"\b{re.escape(word)}\b", content, re.IGNORECASE))

def calculate_words_distance(word1, word2, max_depth=5):
    """Oblicza odległość logiczną między dwoma hasłami."""
    visited = set()
    queue = [(word1, 1)]

    while queue:
        current_article, distance = queue.pop(0)

        if current_article in visited:
            continue
        visited.add(current_article)

        print(f"\nPrzetwarzam artykuł: '{current_article}', aktualna odległość: {distance}")

        page_info = get_article_content_and_links(current_article)
        content = page_info["content"]
        links = page_info["links"]
        if not content:
            print(f"Artykuł '{current_article}' nie ma treści lub nie istnieje.")
            continue

        if contains_words(content, word2):
            print(f"Znaleziono hasło '{word2}' w artykule '{current_article}'.")
            return distance

        if distance < max_depth:
            print(f"Znaleziono {len(links)} odnośników w artykule '{current_article}': {links[:5]}...")
            for link in links:
                if link not in visited:
                    queue.append((link, distance + 1))
        else:
            print(f"Osiągnięto maksymalną głębokość dla artykułu '{current_article}'.")

    print(f"Hasło '{word2}' nie zostało znalezione w podanej głębokości przeszukiwania.")

    return -1


while True:
    print("\nProgram oblicza odległość logiczną między dwoma hasłami na Wikipedii.")
    word1 = input("Podaj pierwsze hasło: ")
    word2 = input("Podaj hasło którego szukasz: ")

    distance = calculate_words_distance(word1, word2)

    if distance == -1:
        print(f"Nie znaleziono hasła '{word2}' w artykule '{word1}' ani w powiązanych artykułach.")
    else:
        print(f"Odległość między hasłami '{word1}' a '{word2}': {distance}")

    try_again = input("Czy chcesz spróbować ponownie? (tak/nie): ").strip().lower()
    while try_again not in ["tak", "nie"]:
        try_again = input("Nie rozumiem, spróbuj ponownie: ").strip().lower()
    if try_again != "tak":
        print("Do zobaczenia!")
        break

