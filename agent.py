"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import config
import trace
from mcp_client import call_tool
from tools import suggest_outfit, create_fit_card, compare_prices
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "price_comparison": None,
        "wardrobe_path": None,
        "dropped_constraint": None,  # set when an empty search was retried looser
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

# ── running it directly ───────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """Run the planning loop and return its visible session state."""
    session = new_session(query, wardrobe)
    try:
        session["parsed"] = _parse_query(session["query"])
        iteration = 0
        while session["fit_card"] is None and session["error"] is None:
            iteration += 1
            trace.check_iterations(iteration)

            if not session["search_results"]:
                parsed = session["parsed"]
                results = call_tool("search_listings", parsed)
                session["search_results"] = results
                trace.step("search_listings (MCP call)", inputs=parsed, returned=results)
                if not results and parsed["size"] is not None:
                    retry_inputs = {
                        "description": parsed["description"],
                        "size": None,
                        "max_price": parsed["max_price"],
                    }
                    results = call_tool("search_listings", retry_inputs)
                    session["search_results"] = results
                    session["dropped_constraint"] = f"size {parsed['size']}"
                    trace.step(
                        "search_listings retry (MCP call)",
                        inputs=retry_inputs,
                        returned=results,
                        note="empty search: dropped size constraint once",
                    )
                if not results:
                    session["error"] = (
                        "No listings matched that request. Try changing the "
                        "description, size, or maximum price."
                    )
                    trace.step(
                        "search branch", returned=session["error"],
                        note="empty results: stopping before suggest_outfit",
                    )
                    break
                session["selected_item"] = session["search_results"][0]

            if session["price_comparison"] is None:
                session["price_comparison"] = compare_prices(
                    session["selected_item"], session["search_results"]
                )
                trace.step(
                    "compare_prices",
                    inputs={
                        "selected_item": session["selected_item"],
                        "search_results": session["search_results"],
                    },
                    returned=session["price_comparison"],
                )

            if session["outfit_suggestion"] is None:
                wardrobe_items = (session["wardrobe"] or {}).get("items", [])
                if wardrobe_items:
                    session["wardrobe_path"] = "saved wardrobe"
                    branch_note = "branch: saved wardrobe"
                else:
                    session["wardrobe_path"] = "general styling"
                    branch_note = "branch: empty wardrobe, general styling"
                trace.step(
                    "wardrobe branch",
                    inputs={"saved_item_count": len(wardrobe_items)},
                    returned=session["wardrobe_path"],
                    note=branch_note,
                )
                session["outfit_suggestion"] = suggest_outfit(
                    session["selected_item"], session["wardrobe"]
                )
                trace.step(
                    "suggest_outfit",
                    inputs={"new_item": session["selected_item"],
                            "wardrobe": session["wardrobe"]},
                    returned=session["outfit_suggestion"],
                )

            if session["fit_card"] is None:
                session["fit_card"] = create_fit_card(
                    session["outfit_suggestion"], session["selected_item"]
                )
                trace.step(
                    "create_fit_card",
                    inputs={"outfit": session["outfit_suggestion"],
                            "new_item": session["selected_item"]},
                    returned=session["fit_card"],
                )
        return session
    except ModelUnavailable as exc:
        session["error"] = f"The model was unavailable, so FitFindr stopped: {exc}"
        return session


def _parse_query(query: str) -> dict:
    """Extract search constraints and leave the item description."""
    text = (query or "").strip()
    working = text
    lowered = working.lower()

    max_price = None
    price_start = -1
    for marker in ("under", "below", "up to", "maximum price", "max price"):
        start = lowered.find(marker)
        if start >= 0 and (price_start < 0 or start < price_start):
            price_start = start
            remainder = working[start + len(marker):].lstrip(" ,:$")
            amount = remainder.split()[0].rstrip(",.") if remainder else ""
            try:
                max_price = float(amount)
            except ValueError:
                max_price = None
            if max_price is not None:
                end = start + len(marker) + len(working[start + len(marker):]) - len(remainder)
                end += len(amount)
                working = working[:start] + " " + working[end:]
                lowered = working.lower()
                break

    size = None
    lowered = working.lower()
    size_start = lowered.find("size ")
    if size_start >= 0:
        phrase_start = size_start
        if size_start >= 3 and lowered[size_start - 3:size_start] == "in ":
            phrase_start = size_start - 3
        after_size = working[size_start + len("size "):].lstrip()
        size = after_size.split()[0].rstrip(",.") if after_size else None
        if size:
            end = size_start + len("size ") + len(working[size_start + len("size "):]) - len(after_size)
            end += len(size)
            working = working[:phrase_start] + " " + working[end:]

    return {
        "description": " ".join(working.strip(" ,").split()),
        "size": size,
        "max_price": max_price,
    }


def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
