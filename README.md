# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> FitFindr now searches the listings, suggests an outfit, and creates a fit
> card. The command above runs the complete agent when the model is available.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

FitFindr accepts a plain-language thrift request such as “a vintage graphic tee
under $30” and searches the local listings data for matching items. It chooses
the best result, suggests outfits using the user’s wardrobe, and creates a
short social-ready fit-card caption. If no listing matches, the planning loop
stops before the model tools and tells the user whether to change the
description, size, or price limit.

---

### Stretch Feature: Price Comparison

I added a fourth tool named `compare_prices`. It will compare the
selected listing with the other search results and return the lowest, highest,
and average prices, plus a short comparison message. The planning loop will
store and display this comparison after searching.

### Stretch Feature: Second Planning Branch

I also added a second planning branch for wardrobe context. If the
session has saved wardrobe items, the loop will take the saved-wardrobe path;
otherwise, it will take a general-styling path and let `suggest_outfit` give
advice without assuming saved pieces. The branch will be visible in the trace
and tested with `--empty-wardrobe`.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the listings data using keywords from the description, an optional size, and an optional maximum price.
- **Inputs:** `description` (`str`) contains the item keywords, describing what the user wants, `size` (`str | None`) is matched case-insensitively, by size token. For example: requested `M` matches `S/M`. `None` disables size filtering;`max_price` (`float | None`) is an inclusive price limit, with `None` disabling price filtering.  
<!-- name and type each: `max_price` (float), not "a price" -->
- **Returns:** The tool returns a list of listing dictionaries containing `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`. Description keywords are matched against the listing’s `title`, `description`, `category`, `style_tags`, `colors`, and `brand`, and results are returned best match first.
- **When it has nothing:** If no listing satisfies the description and optional filters, it returns `[]`, not `None` and not an exception.

### `suggest_outfit`

- **What it does:** Gives suggestions for outfits based on a thrifted item and the user's wardrobe.
- **Inputs:** `new_item` (`dict`) is a listing dictionary; `wardrobe` (`dict`) contains an `items` list of wardrobe item dictionaries with `id`, `name`, `category`, `colors`, `style_tags`, and optional `notes`.
- **Returns:** The tool returns a non-empty string containing one or two outfit ideas that explain how the `new_item` could be styled, based on the given wardrobe and "new_item". When the wardrobe has items, the suggestions should reference pieces from that wardrobe.
- **When it has nothing:** If the wardrobe's `items` list is empty, it should return a non-empty string with general styling advice for the new item instead of raising an exception, or returning `""`.

### `create_fit_card`

- **What it does:** Gives a short caption about the newly suggested fit. Acts like a real post, not just a description of the product.
- **Inputs:** `outfit` (`str`) is an outfit suggestion string returned from `suggest_outfit()`, `new_item` (`dict`) is a listing dictionary for the item.
- **Returns:** Returns a string that is a two to four sentence caption that could work as a real post. It should contain the item, its price, platform, and specific vibe it portrays.
- **When it has nothing:** When `outfit` is empty or only whitespace, it should return a descriptive non-empty message rather than raising an exception or returning `""`.

### `compare_prices`

- **What it does:** Compares the selected listing's price with the listings returned by the same search.
- **Inputs:** `selected_item` (`dict`) is the chosen listing; `search_results` (`list[dict]`) contains the matching listing dictionaries returned by `search_listings`.
- **Returns:** A dictionary containing `selected_item_id`, `selected_price`, `comparison_count`, `lowest_price`, `highest_price`, `average_price`, and `message`.
- **When it has nothing:** If the selected item has no numeric price or the comparison list has no numeric prices, it returns the same keys with unavailable numeric values set to `None`, `comparison_count` set to `0`, and an explanatory `message`.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns no matches, set `session["error"]` and stop. Otherwise, store the first result in `session["selected_item"]`, call `suggest_outfit`, store its result in `session["outfit_suggestion"]`, and then call `create_fit_card`.
**Where it lives:** `agent.py::run_agent`

**Second stretch branch:** After a match, `run_agent` checks the wardrobe. A
non-empty `session["wardrobe"]["items"]` takes the saved-wardrobe path; an
empty list takes the general-styling path. Both paths call `suggest_outfit`,
but the trace names which path was selected and the tool uses the corresponding
wardrobe behavior.

The loop stores each tool result immediately in the session. `suggest_outfit`
reads `session["selected_item"]` and `session["wardrobe"]`, while
`create_fit_card` reads `session["outfit_suggestion"]` and
`session["selected_item"]`; neither handoff relies on a direct result variable.

**How the query is parsed:** <!-- regex, string splitting, or asking the model — say which -->
The agent uses string processing to recognize price phrases such as `under $30` and size phrases such as `size M`. It converts the price to a float, extracts the size, removes those phrases, and uses the remaining words as the description.

**What moves through the session:** <!-- which fields, in what order -->
The original query is stored in `session["query"]`. The parsed description, size, and maximum price are stored in `session["parsed"]`. Search results go into `session["search_results"]`; the first result becomes `session["selected_item"]`; the outfit suggestion becomes `session["outfit_suggestion"]`; and the final caption becomes `session["fit_card"]`. If the search is empty, the explanation is stored in `session["error"]` and the later fields remain empty.

---

## Milestone 1 — MCP Tool Move

I moved `search_listings` from a direct function call into `mcp_server.py`.
The tool is registered with typed inputs for `description`, optional `size`,
and optional `max_price`. `agent.py::run_agent` now calls it through
`mcp_client.call_tool`; the returned listing shape and the rest of the loop
remain unchanged.

The MCP client reported the registered tool:

```
$ python mcp_client.py
Asking mcp_server.py what it offers…

  search_listings
    Search listings by description, optional size, and inclusive dollar ceiling.

    Returns matching listing dictionaries ordered by relevance, or an empty
    list when no listing satisfies all supplied constraints.

    - description: string
    - size: string  (optional)
    - max_price: number  (optional)
```

The end-to-end query then showed the MCP call as the first loop step and still
completed the remaining tools:

```
$ python app.py ask 'vintage graphic tee under $30'
[1] search_listings (MCP call)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[2] compare_prices
      in:  dict with keys: selected_item, search_results
      out: dict with keys: selected_item_id, selected_price, comparison_count, lowest_price, highest_price, average_price
[3] wardrobe branch
      in:  dict with keys: saved_item_count
      out: saved wardrobe
      →    branch: saved wardrobe
[4] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Here are two practical outfits combining your new thrifted Y2K baby tee with pieces from your wardrobe:  **Out…
[5] create_fit_card
      in:  dict with keys: outfit, new_item
      out: Scored this adorable Y2K butterfly baby tee on Depop for just $18, and it's already my new favorite find. I pa…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop
```

The normal query behaved the same after the MCP move: it still reached
`compare_prices`, `suggest_outfit`, and `create_fit_card`, and returned a fit
card. The terminal reported that this particular run used cached model
responses, so the output confirms the MCP rewire and end-to-end behavior, not
model variability.

---

## Milestone 2 — Failure Modes and Loop Trace

I triggered the three failure modes intentionally. The empty-search case made
zero model calls because the loop stopped after the MCP search returned no
listings. The empty-wardrobe case used two cached model responses, but it still
took the empty-wardrobe branch and returned both an outfit suggestion and a fit
card. For the unavailable-model test, I changed one character of the API key
and used a new query; it made one real model call and returned a readable error.
I restored the original key afterward.

**Empty search**

*This output was captured before the retry stretch was added. The same query
now retries once without the size filter before stopping; see Stretch run
evidence below.*

Command: `python app.py ask 'unobtainium moonstone size XXS under $5' --trace`

```
[1] search_listings (MCP call)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[2] search branch
      out: No listings matched that request. Try changing the description, size, or maximum price.
      →    empty results: stopping before suggest_outfit

No listings matched that request. Try changing the description, size, or maximum price.

0 model calls this session
```

**Empty wardrobe**

Command: `python app.py ask 'vintage graphic tee under $30' --empty-wardrobe --trace`

```
[1] search_listings (MCP call)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[2] compare_prices
      in:  dict with keys: selected_item, search_results
      out: dict with keys: selected_item_id, selected_price, comparison_count, lowest_price, highest_price, average_price
[3] wardrobe branch
      in:  dict with keys: saved_item_count
      out: general styling
      →    branch: empty wardrobe, general styling
[4] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Here are two versatile ways to style your Y2K butterfly baby tee:  ### 1. Casual Y2K Streetwear * **The Pieces…
[5] create_fit_card
      in:  dict with keys: outfit, new_item
      out: Scored this adorable Y2K butterfly baby tee on Depop for just $18, and it's giving major nostalgic streetwear …

0 model calls this session, 2 served from cache
```

**Model unavailable**

Command: `python app.py ask 'emerald velvet blazer for a statement evening outfit under $60' --trace`

```
[1] search_listings (MCP call)
      in:  dict with keys: description, size, max_price
      out: 2 items: Velvet Blazer — Emerald Green, Vintage Linen Blazer — Cream
[2] compare_prices
      in:  dict with keys: selected_item, search_results
      out: dict with keys: selected_item_id, selected_price, comparison_count, lowest_price, highest_price, average_price
[3] wardrobe branch
      in:  dict with keys: saved_item_count
      out: saved wardrobe
      →    branch: saved wardrobe

The model was unavailable, so FitFindr stopped: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.

1 model calls this session
```

The failure messages tell the user what happened and, for the empty search,
what to change. The model-unavailable message identifies the key as the next
thing to check instead of exposing a raw stack trace.

**Full normal loop trace**

Command: `python app.py ask 'vintage graphic tee under $30' --trace`

```
[1] search_listings (MCP call)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[2] compare_prices
      in:  dict with keys: selected_item, search_results
      out: dict with keys: selected_item_id, selected_price, comparison_count, lowest_price, highest_price, average_price
[3] wardrobe branch
      in:  dict with keys: saved_item_count
      out: saved wardrobe
      →    branch: saved wardrobe
[4] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Here are two practical outfits combining your new thrifted Y2K baby tee with pieces from your wardrobe:  **Out…
[5] create_fit_card
      in:  dict with keys: outfit, new_item
      out: Scored this adorable Y2K butterfly baby tee on Depop for just $18, and it's already my new favorite find. I pa…

Found: Y2K Baby Tee — Butterfly Print — $18.0 on depop
```

The trace shows the tool calls in order, including the MCP call, and the empty
search trace is shorter because the loop stops before `compare_prices`,
`suggest_outfit`, and `create_fit_card`.

---

## Unit 4 Stretch Plan

Before implementing it, I declared the optional **retry with looser
constraints** stretch. When a search with a requested size returns no listings,
the agent retries once without the size filter and records that dropped
constraint in the trace.

**Stretch run evidence**

Command: `python app.py ask 'unobtainium moonstone size XXS under $5' --trace`

```
[1] search_listings (MCP call)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[2] search_listings retry (MCP call)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    empty search: dropped size constraint once
[3] search branch
      out: No listings matched that request. Try changing the description, size, or maximum price.
      →    empty results: stopping before suggest_outfit

  Nothing matched in size XXS, so FitFindr searched once more without the size filter.

  No listings matched that request. Try changing the description, size, or maximum price.

0 model calls this session
```

The retry kept the description and price ceiling, removed only `size`, and
still stopped safely when the second search was empty. At first the trace was
the only place that recorded the dropped constraint. I then added
`session["dropped_constraint"]` in `agent.py::run_agent`, and `app.py` now
prints it, so the user is told which filter was removed.

**Stretch run log**

The retry was added after the before and after runs, so neither of those logs
shows it. I ran a separate evaluation to measure it, with
`python run_eval.py --label retry` (`results/run_2026-10-07_2213_retry.md`).
It is evidence for this stretch only. It is not a third measurement of the
improvement. I added one diagnostic scenario to `scenarios.py`,
`denim jacket size XXL under $50`. No denim jacket is listed in XXL, but seven
matches exist once the size is dropped, so this query shows the retry actually
finding something. I also added a `dropped_constraint` line to each try in
the `run_eval.py` report.

A try passes if the trace shows `search_listings retry (MCP call)`, the log
records the dropped constraint, and the loop then takes the correct path:
continue to a fit card if the retry found listings, or stop before
`suggest_outfit` if it didn't.

| Scenario | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| Retry finds results (`denim jacket size XXL under $50`) | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| Retry still empty (`designer ballgown size XXS under $5`, Criterion 2's query) | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

In all five denim tries, the log recorded `dropped_constraint: size XXL`, the
retry returned 7 listings, and the run went on to select
`Denim Jacket — Light Wash, Cropped` (`lst_007`) and produce a fit card. In all
five ballgown tries, the log recorded `dropped_constraint: size XXS`, the retry
returned nothing, and the loop stopped before `suggest_outfit`. So Criterion 2
still holds with the retry in place, with one extra search step. In the same
run, criteria 1, 3, 4, and 5 also passed 5 of 5, so the retry didn't break
anything.

Real output from Try 1 of the denim scenario, from
`results/run_2026-10-07_2213_retry.md`, produced by `run_eval.py::run_once`
calling `agent.py::run_agent`:

```
- stopped early: no
- selected_item: Denim Jacket — Light Wash, Cropped ($42.0, poshmark)
- search_results: 7
- dropped_constraint: size XXL

[1] search_listings (MCP call)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[2] search_listings retry (MCP call)
      in:  dict with keys: description, size, max_price
      out: 7 items: Denim Jacket — Light Wash, Cropped, Vintage Levi's 501 Jeans — Medium Wash, 90s Track Jacket — Navy/White Stripe … +4 more
      →    empty search: dropped size constraint once
[3] compare_prices
      in:  dict with keys: selected_item, search_results
      out: dict with keys: selected_item_id, selected_price, comparison_count, lowest_price, highest_price, average_price
[4] wardrobe branch
      in:  dict with keys: saved_item_count
      out: saved wardrobe
      →    branch: saved wardrobe
[5] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Here is a practical, stylish outfit using your new thrifted item:  **Outfit: Streetwear Denim-on-Denim** *   *…
[6] create_fit_card
      in:  dict with keys: outfit, new_item
      out: Nothing beats the retro-cool streetwear energy of throwing on a Denim Jacket — Light Wash, Cropped over a cris…
```

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30' --trace
[1] search_listings
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[2] compare_prices
      in:  dict with keys: selected_item, search_results
      out: dict with keys: selected_item_id, selected_price, comparison_count, lowest_price, highest_price, average_price
[3] wardrobe branch
      in:  dict with keys: saved_item_count
      out: saved wardrobe
      →    branch: saved wardrobe
[4] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Here are two practical outfits combining your new thrifted Y2K baby tee with pieces from your wardrobe:  **Out…
[5] create_fit_card
      in:  dict with keys: outfit, new_item
      out: Scored this adorable Y2K butterfly baby tee on Depop for just $18, and it's already my new favorite find. I pa…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here are two practical outfits combining your new thrifted Y2K baby tee with pieces from your wardrobe:

**Outfit 1: Y2K Streetwear Casual**
*   **Top:** Y2K Butterfly Baby Tee
*   **Bottoms:** Baggy straight-leg jeans (dark wash)
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Black crossbody bag
*   **Why it works:** The fitted, cropped silhouette of the baby tee balances the oversized, high-waisted baggy jeans for a classic Y2K streetwear proportion. The white in the sneakers ties the white graphic of the tee together seamlessly.

**Outfit 2: Casual Earth-Tones Minimal**
*   **Top:** Y2K Butterfly Baby Tee
*   **Bottoms:** Wide-leg khaki trousers
*   **Outerwear:** Vintage black denim jacket (worn over the top)
*   **Shoes:** Chunky white sneakers
*   **Why it works:** The pink and purple butterfly print pops against neutral khaki trousers. Layering the slightly cropped black denim jacket keeps the waistline defined while adding a grounded, vintage contrast to the soft pastels of the tee.

  Fit card: Scored this adorable Y2K butterfly baby tee on Depop for just $18, and it's already my new favorite find. I paired it with baggy dark-wash denim and chunky sneakers for the ultimate nostalgic streetwear moment. It gives off the best effortless, early-2000s downtown vibe.


```

**The three tools (plus a stretch tool), tested one at a time**

```
(.venv) meznu@BillyLaptop:/mnt/c/CodePath_AI-2/ai201-project2-fitfindr-starter-v2026$ python -c 'from tools import search_listings; print(search_listings("graphic tee", max_price=30))'
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}]
```

```
(.venv) meznu@BillyLaptop:/mnt/c/CodePath_AI-2/ai201-project2-fitfindr-starter-v2026$ python -c 'from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))'
Here is a practical everyday outfit featuring your new thrifted jeans:

**The Outfit:**
*   **Top:** White ribbed tank top
*   **Bottoms:** Vintage Levi's 501 Jeans (Medium wash)
*   **Outerwear:** Oversized grey crewneck sweatshirt
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Black crossbody bag

**Why it works:**
The fitted white ribbed tank creates a clean, classic base that balances the relaxed straight leg of the Levi's 501s. Layering the oversized grey crewneck on top plays with proportions—the cozy, slouchy grey contrasts nicely with the structured vintage denim. Finally, the chunky white sneakers and black crossbody bag tie the streetwear aesthetic together for an effortless, comfortable look.
```

```
(.venv) meznu@BillyLaptop:/mnt/c/CodePath_AI-2/ai201-project2-fitfindr-starter-v2026$ python -c 'from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card("jeans and white sneakers", load_listings()[0]))'
Nothing beats the structure of a classic pair of vintage Levi's 501s styled with fresh white sneakers for that effortless off-duty look. I just scored this medium-wash dream on Depop for $38, and they fit like an absolute glove. Seriously obsessed with how comfortable and timeless this casual weekend fit feels!
```

Running the above prompt 3 different times resulted in the same output each time due to `CACHE_ENABLED` being activated. I reran the same tool for 3 more iterations using `AI201_CACHE=0` resulting in 3 uncached captions which were all slightly different from each other:

```
(.venv) meznu@BillyLaptop:/mnt/c/CodePath_AI-2/ai201-project2-fitfindr-starter-v2026$ AI201_CACHE=0 python -c 'from tools import create_fit_card; from utils.data_loader import load_listings; item=load_listings()[0]; print(create_fit_card("jeans and white sneakers", item)); print("--- SECOND RUN ---"); print(create_fit_card("jeans and white sneakers", item)); print("--- THIRD RUN ---"); print(create_fit_card("jeans and white sneakers", item))'
Just scored these vintage medium-wash Levi's 501s on Depop for $38, and they are the ultimate closet staple. I paired them with my favorite white sneakers for that effortlessly cool, 90s off-duty model vibe. Honestly, nothing beats a perfectly broken-in pair of denim.
--- SECOND RUN ---
Scored these vintage Levi's 501s on Depop for just $38 and they fit like an absolute dream. Threw them on with crisp white sneakers for that effortlessly cool, 90s off-duty look. Nothing beats the wash and wear of a truly broken-in pair of denim.
--- THIRD RUN ---
Scored these vintage Levi's 501s on Depop for just $38 and I'm obsessed. Paired with crisp white sneakers, they give off that effortless, off-duty model aesthetic. It's the ultimate everyday uniform that never goes out of style.
```

---

**Stretch tool:** `compare_prices`

```text
$ python -c 'from tools import compare_prices, search_listings; results=search_listings("graphic tee", max_price=30); print(compare_prices(results[0], results))'
{'selected_item_id': 'lst_002', 'selected_price': 18.0, 'comparison_count': 6, 'lowest_price': 15.0, 'highest_price': 27.0, 'average_price': 21.5, 'message': 'The selected item is $18.00, below the search average of $21.50.'}
```

**Stretch branch:** Empty wardrobe
```
$ python app.py ask 'vintage graphic tee under $30' --empty-wardrobe --trace
(running with an empty wardrobe)
[1] search_listings
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[2] compare_prices
      in:  dict with keys: selected_item, search_results
      out: dict with keys: selected_item_id, selected_price, comparison_count, lowest_price, highest_price, average_price
[3] wardrobe branch
      in:  dict with keys: saved_item_count
      out: general styling
      →    branch: empty wardrobe, general styling
[4] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Here are two versatile ways to style your Y2K butterfly baby tee:  ### 1. Casual Y2K Streetwear * **The Pieces…
[5] create_fit_card
      in:  dict with keys: outfit, new_item
      out: Scored this adorable Y2K butterfly baby tee on Depop for just $18, and it's giving major nostalgic streetwear …

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here are two versatile ways to style your Y2K butterfly baby tee:

### 1. Casual Y2K Streetwear
* **The Pieces:** Relaxed low-rise or mid-rise straight-leg blue jeans, and retro sneakers (like chunky trainers or canvas low-tops).
* **Styling Logic:** A baby tee has a naturally fitted, cropped silhouette, so pairing it with looser bottoms creates a flattering proportional contrast. The denim keeps the look grounded while leaning into the nostalgic 2000s aesthetic of the graphic.

### 2. Sweet & Edgy Mix
* **The Pieces:** A flowy black or pastel midi skirt (satin or tiered cotton) and chunky combat boots or strappy sandals.
* **Styling Logic:** This bridges the tee's "y2k" and "cottagecore" tags. The fitted top balances the volume of a skirt, while the juxtaposition of a girly butterfly print with tougher boots creates an effortless, balanced outfit.

  Fit card: Scored this adorable Y2K butterfly baby tee on Depop for just $18, and it's giving major nostalgic streetwear energy. I love styling it with relaxed straight-leg jeans for that classic 2000s proportion play. It’s such an effortless piece to throw on for a sweet yet edgy everyday look.

```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I asked Codex to check whether the evaluation report actually measured all five acceptance criteria well enough for the rubric.
- *What came back:* It found that the original `run_eval.py` report showed only the selected item and result count, so it did not directly prove the exact state handoff for criterion 3 or every returned price for criterion 5.
- *What I changed:* I updated `run_eval.py` to record the selected-item ID, the item received by `suggest_outfit`, exact equality of those dictionaries, the parsed price ceiling, every returned price, and whether each price was within the ceiling.

**Moment 2**

- *What I asked for:* I asked Codex for a measured improvement even though the baseline missed none of the five criteria.
- *What came back:* The review found that the fit-card criterion only required one word from the listing title, so the prompt could be made more specific without changing the original criterion.
- *What I changed:* I changed `tools.py::create_fit_card` to ask for the exact listing title phrase while retaining the requirements for a two-to-four-sentence caption, price, platform, and outfit vibe.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Full three-tool run returns a fit card | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Empty search stops before tool 2 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Item in session matches item passed on | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card mentions the item's details | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Over-budget query returns nothing over the limit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Real output from one try**, pasted as text. This excerpt came from
`results/run_2026-10-07_1813_before.md`, produced by
`run_eval.py::run_once` calling `agent.py::run_agent`; the fit card text came
from `tools.py::create_fit_card`:

```
**Try 1**
- stopped early: no
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
- search_results: 10
- selected_item_id: lst_002
- suggest_outfit_new_item_id: lst_002
- state_handoff_exact_equal: True
- max_price: 30.0
- returned_prices: [18.0, 24.0, 19.0, 26.0, 15.0, 22.0, 27.0, 20.0, 30.0, 12.0]
- all_returned_prices_within_max: True

Fit card:
Scored this butterfly print Y2K baby tee on Depop for just $18, and I am obsessed. It gives off the ultimate soft-meets-grunge vibe whether you style it with baggy denim or wide-leg trousers. FitFindr makes curating these nostalgic looks way too easy!
```

**Criterion 2, Try 1** (query `designer ballgown size XXS under $5`). This came
from the same file, produced by `run_eval.py::run_once` calling
`agent.py::run_agent`; the stop message and the trace come from the search
branch in `run_agent`:

```
- stopped early: yes — No listings matched that request. Try changing the description, size, or maximum price.
- selected_item: (none)
- search_results: 0
- suggest_outfit_new_item_id: (not called)

[1] search_listings (MCP call)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[2] search branch
      out: No listings matched that request. Try changing the description, size, or maximum price.
      →    empty results: stopping before suggest_outfit
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Full three-tool run returns a fit card | 4 of 5 | MET (5/5) | All five matching-query tries reached `create_fit_card` and returned a non-empty card. |
| 2 | Empty search stops before tool 2 | 5 of 5 | MET (5/5) | Every impossible query returned the requested message and stopped after the empty MCP search. |
| 3 | Item in session matches item passed on | 5 of 5 | MET (5/5) | All five tries recorded `state_handoff_exact_equal: True`; the selected ID and outfit-input ID were both `lst_002`. |
| 4 | Fit card mentions the item's details | 4 of 5 | MET (5/5) | Every card was 2–4 sentences and included a title word, `$18`, and `Depop` (case-insensitive). |
| 5 | Over-budget query returns nothing over the limit | 5 of 5 | MET (5/5) | Every returned price in all five tries was at most the parsed `$30` ceiling. |

**Diagnoses**

There were no misses in this baseline, so there is no failing mechanism to
diagnose. The results do show that Criterion 1's 4-of-5 target was
conservative: the matching run passed 5 of 5 times. A tighter, still
checkable target for a future run would be 5 of 5 matching queries completing
all three tools. I am leaving the original criterion unchanged because this
is a target-tightening observation, not a revision of a broken criterion.

Criterion 4 was set too low in two ways. Its 4-of-5 target passed 5 of 5,
and "a word from the listing's `title`" is easy to satisfy: a generic word
like "tee" counts. Not one of the five baseline cards used the actual listing
title (`Y2K Baby Tee — Butterfly Print`). Each one paraphrased it as "butterfly
baby tee." The cause is the prompt in `tools.py::create_fit_card`. It never
asked for the title, so the model was free to rename the item. A tighter target
would be: **in 5 of 5 tries, the fit card contains the exact listing title.**
This weakness is what my improvement targets.



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
[1] search_listings (MCP call)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
[2] compare_prices
      in:  dict with keys: selected_item, search_results
      out: dict with keys: selected_item_id, selected_price, comparison_count, lowest_price, highest_price, average_price
[3] wardrobe branch
      in:  dict with keys: saved_item_count
      out: saved wardrobe
      →    branch: saved wardrobe
[4] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Here are two practical outfits combining your new thrifted Y2K baby tee with pieces from your wardrobe:  **Out…
[5] create_fit_card
      in:  dict with keys: outfit, new_item
      out: Scored this adorable Y2K butterfly baby tee on Depop for just $18, and it's already my new favorite find. I pa…
```

**Empty search**

*This trace was captured before the retry stretch was added. The same query
now retries once without the size filter before stopping; see Stretch run
evidence in the Unit 4 Stretch Plan.*

```
[1] search_listings (MCP call)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[2] search branch
      out: No listings matched that request. Try changing the description, size, or maximum price.
      →    empty results: stopping before suggest_outfit
```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->

`mcp_server.py` registers `search_listings`, and `agent.py::run_agent` calls it
through `mcp_client.call_tool`. The MCP result had the same listing shape as
the direct tool result, and the normal query still completed all downstream
steps. The trace above shows the MCP call in position 1.



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

I changed `tools.py::create_fit_card` so its prompt asks for the exact listing
title phrase, rather than only requiring a word from the title. The baseline
had no misses, but this makes the fit-card requirement more specific and
strengthens the behavior behind Criterion 4.

**Which failure it was meant to fix:**

There was no failing criterion to repair. The diagnosis above found that
Criterion 4's target was too loose: the prompt never asked for the listing
title, and 0 of 5 baseline cards used it. This change aims at the tighter
target named there ("exact listing title in 5 of 5 cards"). The original
criterion stays as written.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Full three-tool run returns a fit card | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Empty search stops before tool 2 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Item in session matches item passed on | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card mentions the item's details | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Over-budget query returns nothing over the limit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Did it help, and how do I know:**

Yes, for the target it was aimed at. The original five criteria passed 5 of 5
in both runs, so the verdicts didn't change. I measured the tighter target by
searching both logs for the exact title `Y2K Baby Tee — Butterfly Print`:

| Measure (Criterion 4 scenario) | Before | After |
|---|---|---|
| Card contains the exact listing title | 0 of 5 | 5 of 5 |
| Card is 2–4 sentences, has `$18` and Depop | 5 of 5 | 5 of 5 |

The same held across every Y2K-tee scenario (criteria 1, 3, 4, 5): 0 of 20
cards used the exact title before and 20 of 20 after. Neither run had
model-service errors, so the comparison is usable.

**A side effect, reported honestly:** the cards became more alike. In the
before log, no card or outfit text contains "Channeling." In the after log it
appears 26 times, and all 5 Criterion 4 cards open with "Channel…" or
"Channeling…". My guess is that forcing a fixed, awkward title into the
caption pushed the model toward one safe opening. So the change made the card
more accurate, and slightly worse as something a person would want to post.

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

No required criterion remains missed, but the tests are weaker than the 5/5
scores make them look:

- **The scenarios barely vary.** Criteria 1, 3, 4, and 5 all run a Y2K-tee
  query, so every try selects the same listing (`lst_002`). Criterion 5's search
  is deterministic, which means its five tries are identical by design. I'd
  rewrite these to cover five different items and price ceilings. I stopped
  because the criteria were already committed with these scenarios. Changing
  them now would be a second change to the system.
- **The agent always picks the first search result.** Keyword ranking isn't a
  quality check. For `graphic tee` under $30, it put `Mesh Long-Sleeve Top`
  (which isn't a graphic tee) ahead of `Vintage Band Tee — Faded Grey`. Nothing
  checks that the top result is actually the best one.
- **The fit cards sound alike after the improvement.** Many open with
  "Channeling…" (see above). The next prompt change would ask for a varied
  opening, measured the same way as the first improvement.
- **The retry can hand back the wrong size.** For `denim jacket size XXL`, it
  selects a size S jacket. The CLI now says the size filter was dropped, but
  the outfit suggestion and fit card never mention that the item may not fit.
  A fix would pass `dropped_constraint` into `suggest_outfit` so it can flag
  the mismatch. I stopped there because the stretch only asks for the retry and
  a note on what it dropped.



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
