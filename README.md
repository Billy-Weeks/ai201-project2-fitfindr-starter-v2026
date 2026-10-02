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
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
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

The loop stores each tool result immediately in the session. `suggest_outfit`
reads `session["selected_item"]` and `session["wardrobe"]`, while
`create_fit_card` reads `session["outfit_suggestion"]` and
`session["selected_item"]`; neither handoff relies on a direct result variable.

**How the query is parsed:** <!-- regex, string splitting, or asking the model — say which -->
The agent uses string processing to recognize price phrases such as `under $30` and size phrases such as `size M`. It converts the price to a float, extracts the size, removes those phrases, and uses the remaining words as the description.

**What moves through the session:** <!-- which fields, in what order -->
The original query is stored in `session["query"]`. The parsed description, size, and maximum price are stored in `session["parsed"]`. Search results go into `session["search_results"]`; the first result becomes `session["selected_item"]`; the outfit suggestion becomes `session["outfit_suggestion"]`; and the final caption becomes `session["fit_card"]`. If the search is empty, the explanation is stored in `session["error"]` and the later fields remain empty.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask '...'

```

**The three tools, tested one at a time**

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
(.venv) meznu@BillyLaptop:/mnt/c/CodePath_AI-2/ai201-project2-fitfindr-starter-v2026$ AI201_CACHE=0 python -c 'from tools import create_fit_card; from utils.data_loader import load_listings; item=load_listings()[0]; print(create_fit_card("jeans and white sneakers", item));
--- FIRST RUN ---
Just scored these vintage medium-wash Levi's 501s on Depop for $38, and they are the ultimate closet staple. I paired them with my favorite white sneakers for that effortlessly cool, 90s off-duty model vibe. Honestly, nothing beats a perfectly broken-in pair of denim.
--- SECOND RUN ---
Scored these vintage Levi's 501s on Depop for just $38 and they fit like an absolute dream. Threw them on with crisp white sneakers for that effortlessly cool, 90s off-duty look. Nothing beats the wash and wear of a truly broken-in pair of denim.
--- THIRD RUN ---
Scored these vintage Levi's 501s on Depop for just $38 and I'm obsessed. Paired with crisp white sneakers, they give off that effortless, off-duty model aesthetic. It's the ultimate everyday uniform that never goes out of style.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

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
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

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
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



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

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



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
