"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────
_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "find",
    "for",
    "from",
    "have",
    "i",
    "in",
    "is",
    "item",
    "looking",
    "me",
    "need",
    "of",
    "on",
    "or",
    "please",
    "search",
    "show",
    "something",
    "that",
    "the",
    "to",
    "want",
    "with",
}


def _keywords(text: str) -> set[str]:
    """Return lowercase words worth matching, with stopwords removed."""

    words = re.findall(r"[a-z0-9']+", (text or "").lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 1}

def _size_tokens(size: str) -> set[str]:
    """Normalize slash-separated size labels for comparison."""
    cleaned = re.sub(r"\([^)]*\)", " ", size or "")  # drop parentheticals
    parts = [p.strip().upper() for p in cleaned.split("/")]
    return {p for p in parts if p}

def _size_matches(wanted: str, listing_size: str) -> bool:
    if not wanted:
        return True
    listing_tokens = _size_tokens(listing_size)
    if any(token.startswith("ONE SIZE") for token in listing_tokens):
        return True
    return bool(_size_tokens(wanted) & listing_tokens)


def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    wanted_keywords = _keywords(description)
    if not wanted_keywords:
        return []

    matches: list[tuple[int, int, dict]] = []
    for position, listing in enumerate(load_listings()):
        price = listing.get("price")
        if max_price is not None and (price is None or price > max_price):
            continue
        if size is not None and not _size_matches(size, listing.get("size", "")):
            continue

        searchable_parts = [
            listing.get("title", ""),
            listing.get("description", ""),
            listing.get("category", ""),
            " ".join(listing.get("style_tags", [])),
            " ".join(listing.get("colors", [])),
            listing.get("brand") or "",
        ]
        listing_keywords = _keywords(" ".join(searchable_parts))
        score = len(wanted_keywords & listing_keywords)
        if score:
            matches.append((score, -position, listing))

    matches.sort(reverse=True, key=lambda match: (match[0], match[1]))
    return [listing for _, _, listing in matches[: config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    item_text = (
        f"Title: {new_item.get('title', 'unnamed item')}\n"
        f"Description: {new_item.get('description', '')}\n"
        f"Category: {new_item.get('category', '')}\n"
        f"Colors: {', '.join(new_item.get('colors', []))}\n"
        f"Style tags: {', '.join(new_item.get('style_tags', []))}\n"
        f"Size: {new_item.get('size', '')}"
    )
    wardrobe_items = (wardrobe or {}).get("items", [])
    if wardrobe_items:
        wardrobe_text = "\n".join(
            "- "
            + ", ".join(
                str(value)
                for value in (
                    item.get("name", ""),
                    item.get("category", ""),
                    ", ".join(item.get("colors", [])),
                    ", ".join(item.get("style_tags", [])),
                    item.get("notes", ""),
                )
                if value
            )
            for item in wardrobe_items
        )
        prompt = (
            "Suggest one or two practical outfits using the thrifted item and "
            "the user's existing wardrobe. Name specific wardrobe pieces, "
            "explain why the colors or styles work, and keep the advice concise.\n\n"
            f"THRIFTED ITEM:\n{item_text}\n\nWARDROBE:\n{wardrobe_text}"
        )
        system = "You are a helpful personal stylist. Use only the wardrobe pieces provided."
    else:
        prompt = (
            "Give one or two general outfit ideas for this thrifted item. The "
            "user has no saved wardrobe items, so recommend versatile categories "
            "of pieces and explain the styling logic. Keep the advice concise.\n\n"
            f"THRIFTED ITEM:\n{item_text}"
        )
        system = "You are a helpful personal stylist giving useful advice without assuming a saved wardrobe."

    return generate(prompt, system=system).strip()


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not outfit or not outfit.strip():
        return "No fit card could be created because the outfit suggestion was empty."

    item_title = new_item.get("title", "this thrift find")
    price = new_item.get("price", "unknown price")
    platform = new_item.get("platform", "the resale marketplace")
    prompt = (
        "Write a social-media-ready FitFindr caption in exactly two to four "
        "sentences. Mention the item, its price, and its platform once, and "
        "describe the outfit's specific vibe. Sound natural and enthusiastic, "
        "not like a product listing. Do not add headings or bullet points.\n\n"
        f"ITEM: {item_title}\n"
        f"PRICE: ${price}\n"
        f"PLATFORM: {platform}\n"
        f"OUTFIT SUGGESTION: {outfit}"
    )
    return generate(
        prompt,
        system="You write concise, authentic thrift-fashion captions.",
    ).strip()


# ── Stretch tool: compare_prices ────────────────────────────────────────────

def compare_prices(selected_item: dict, search_results: list[dict]) -> dict:
    """Compare the selected listing's price with the search results."""
    selected_price = selected_item.get("price") if selected_item else None
    prices = [
        listing.get("price")
        for listing in (search_results or [])
        if isinstance(listing.get("price"), (int, float))
    ]

    if not isinstance(selected_price, (int, float)) or not prices:
        return {
            "selected_item_id": (selected_item or {}).get("id"),
            "selected_price": None,
            "comparison_count": 0,
            "lowest_price": None,
            "highest_price": None,
            "average_price": None,
            "message": "Price comparison is unavailable for these listings.",
        }

    average_price = round(sum(prices) / len(prices), 2)
    if selected_price < average_price:
        position = "below"
    elif selected_price > average_price:
        position = "above"
    else:
        position = "at"

    return {
        "selected_item_id": selected_item.get("id"),
        "selected_price": selected_price,
        "comparison_count": len(prices),
        "lowest_price": min(prices),
        "highest_price": max(prices),
        "average_price": average_price,
        "message": (
            f"The selected item is ${selected_price:.2f}, {position} the "
            f"search average of ${average_price:.2f}."
        ),
    }
