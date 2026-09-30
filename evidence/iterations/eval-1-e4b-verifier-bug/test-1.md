# test-1: What was the SBIC program and how did it multiply venture capital?

| | |
|---|---|
| Mode | ask · **local** execution |
| Model | `gemma4:e4b-it-qat` |
| Network during run | **online** |
| Retrieval | hybrid: bm25 + embeddinggemma:300m (RRF) (0.05s) |
| Model time | 8.32s |
| Memory | {"ollama_loaded": [{"model": "gemma4:e4b-it-qat", "size_gb": 5.41, "gpu_gb": 5.41}, {"model": "embeddinggemma:300m", "size_gb": 0.68, "gpu_gb": 0.68}], "ollama_process_rss_gb": 0.02, "system_used_gb": 14.72} |

## Expected (written before the run)

- Test type: direct, one source
- Expected behavior: `answer`
- Expected passages: `week-2-section:s13`
- Expected answer: The Small Business Investment Company program, created by the 1958 Small Business Investment Act. The federal government licensed private investment funds and lent roughly $2-$3 of low-cost government money for every $1 of private capital, which multiplied the early risk-capital pool and seeded the Valley's first VC firms.

## Retrieved passages (what Gemma was shown)

**[1] Week 2 Section, slide 13 (part 1)** · `raw/POLECON156_Week2_DiscussionSection.pptx` · id `week-2-section:s13` · source  
<sub>rrf=0.0328, bm25 rank=1, embedding rank=1, cosine=0.58</sub>

> Venture capital — why it mattered, and why it stayed closed
> • It financed the un-financeable. A bank wants collateral and steady repayment; a startup has neither. Venture capital put in equity, took a board seat, and absorbed the loss when a company failed — which made funding high-risk ventures possible at all.
> • The government primed the pump — the SBIC. The 1958 Small Business Investment Act created the Small Business Investment Company program: the federal government licensed private investment funds and leveraged them, lending roughly $2–$3 of low-cost government money for every $1 of private capital. It multiplied the early risk-capital pool and seeded the Valley's first firms (Draper, Gaither & Anderson, 1959).
> • But it became a closed circle. Venture capital is still an insular “old-boys network.” Many partners are former founders who back people like themselves; talent is evenly distributed, opportunity is not. Some rise in East and South Asian representation — very few Latino or Black investors. Who hears about a deal, and who gets the introduction, still favors insiders.
> John Doerr, on “pattern recognition” (O'Mara, p. 75): backing “white male nerds who dropped out of Harvard or Stanford and have no social life.”

**[2] Week 2 Section, slide 13 (part 2)** · `raw/POLECON156_Week2_DiscussionSection.pptx` · id `week-2-section:s13.2` · source  
<sub>rrf=0.0323, bm25 rank=2, embedding rank=2, cosine=0.49</sub>

> Venture capital — why it mattered, and why it stayed closed
> Speaker notes: Fund structure and the 'good VC' checklist are deliberately left out. Focus: why VC exists, the SBIC as government scaffolding, the diversity problem.

**[3] Week 2 Section, slide 5 (part 1)** · `raw/POLECON156_Week2_DiscussionSection.pptx` · id `week-2-section:s5` · source  
<sub>rrf=0.0308, bm25 rank=3, embedding rank=7, cosine=0.34</sub>

> The five pillars
> 1 · The state / government policy War and great-power competition have driven US innovation for 80 years. Federal and military money — WWII, the Cold War, Vannevar Bush's push for permanent research funding, Sputnik → NASA / ARPA / NDEA — built the foundation. In 1958, ~80% of Fairchild's business was government contracts.
> 2 · Research universities They supply the people. Stanford above all — Terman's applied-engineering culture, the Research Park, the faculty–student–industry loop — plus Berkeley, San José State, UCSF (biotech), Santa Clara (law).
> 3 · Venture capital Funding for ventures banks would never touch. Georges Doriot (1946), then the federal SBIC program (1958) that leveraged private risk capital, then the Valley's own firms from 1959. Decisive — but an insular network.
> 4 · Immigrants ~25% of US high-tech firms had an immigrant founder; ~40% of Valley firms by the internet era; ~44% of Bay Area residents are foreign-born. Berkeley and Stanford are the main pipelines.
> 5 · The legal system Valley law firms took equity instead of fees and built the scaffolding — incorporation, term sheets, M&A, IPOs. California's refusal to enforce non-competes keeps talent moving.
> Running through all five: a transversal counterculture / anti-establishment ethos (see later).

**[4] Week 2 Section, slide 9** · `raw/POLECON156_Week2_DiscussionSection.pptx` · id `week-2-section:s9` · source  
<sub>rrf=0.0308, bm25 rank=5, embedding rank=5, cosine=0.34</sub>

> Written reflection
> TODAY'S PROMPT
> Why was the venture capital industry so critical to Silicon Valley's rise?
> And, according to the first three chapters of The Code, what was the first “venture capitalist” entity in Silicon Valley?
> Instructions
> • 7 minutes (+2 to upload)
> • Handwritten in your spiral notebook — no devices, open-book.
> • One short paragraph per question — BOTH answers on the SAME single page.
> • When you're done, take a photo and upload it to bCourses under this week's reflection.
> Speaker notes: Reflection is graded randomly — students don't know which weeks. 4 pts (2 quality of answers, 2 thoughtfulness). Reinforce verbally: ONE page, both answers. The 'entity' wording nudges them past just naming a person.

**[5] Week 2 Section, slide 17** · `raw/POLECON156_Week2_DiscussionSection.pptx` · id `week-2-section:s17` · source  
<sub>rrf=0.0289, bm25 rank=6, embedding rank=13, cosine=0.31</sub>

> Summary
> THE FIVE PILLARS
> • The state — military and federal money seeded it
> • Universities — Stanford's model supplied the people
> • Venture capital — financed the un-financeable, then closed ranks
> • Immigrants — a growing share of every founding cohort
> • The legal system — equity-taking firms, no non-competes
> …and a counterculture ethos running through all five.
> BEFORE YOU GO
> • Upload your reflection to bCourses — one single page
> • Attendance = your Poll Everywhere response
> • One free discretionary absence — email in advance
> • Devices away unless told otherwise
> • Next week: Apple, Microsoft, Steve Jobs

**[6] Week 2 Section, slide 12 (part 1)** · `raw/POLECON156_Week2_DiscussionSection.pptx` · id `week-2-section:s12` · source  
<sub>rrf=0.0288, bm25 rank=7, embedding rank=12, cosine=0.31</sub>

> Who's who
> Vannevar Bush — Ran WWII federal R&D; “Science, the Endless Frontier” (1945) → permanent federal science funding.
> Georges Doriot — The first venture capitalist — Harvard Business School professor; ARDC (1946); funded DEC.
> Fred Terman — “Father of Silicon Valley”; brought the MIT military/industry model to Stanford; built the Research Park.
> Hewlett & Packard — Terman's students; founded HP in a Palo Alto garage (1939).
> Ann Hardy — Built commercial nationwide time-sharing at Tymshare; underpaid and overlooked.
> William Shockley — Co-invented the transistor (Nobel 1956); Shockley Semiconductor (1956) brought silicon to the Valley.
> The “Traitorous Eight” — Quit Shockley in 1957 → Fairchild. Incl. Noyce, Moore, Kleiner. “Fairchildren” seeded the Valley.
> Arthur Rock — Financed the Eight's move; made “venture capitalist” a job title; funded and chaired Intel.
> Andy Grove — Hungarian refugee; Intel #3, later CEO; chips as “high-tech jelly beans.”
> Lee Felsenstein — Cal EECS; MC of the Homebrew Computer Club; designed the Osborne 1, the first mass-produced portable.
> Pam Hardt-English — Cal CS dropout; led Community Memory — a public computer terminal in a Berkeley record store.
> Mario Savio — Leader of the Berkeley Free Speech Movement (1964); the “bodies upon the gears” speech.
> Clark Kerr — UC President; 1960 California Master Plan; fired by the Regents in 1967 after Reagan's election.


## Gemma's answer

- The 1958 Small Business Investment Act created the Small Business Investment Company program, which was a federal government licensing of private investment funds [1]. [1]
- The SBIC program leveraged low-cost government money, lending roughly $2–$3 for every $1 of private capital [1]. [1]
- This leveraging multiplied the early risk-capital pool and helped seed the Valley's first firms, such as Draper, Gaither & Anderson, in 1959 [1]. [1]

## Citation checks (automatic)

| Claim | Cites | Numbers missing from cited text | Word overlap | Verdict |
|---|---|---|---|---|
| The 1958 Small Business Investment Act created the Small Business Investment Company progr… | [1] | — | 0.86 | supported |
| The SBIC program leveraged low-cost government money, lending roughly $2–$3 for every $1 o… | [1] | — | 0.94 | supported |
| This leveraging multiplied the early risk-capital pool and helped seed the Valley's first … | [1] | — | 0.71 | supported |

## Automatic assessment

```json
{
  "retrieval_found_expected": true,
  "expected_passage_ranks": {
    "week-2-section:s13": 1
  },
  "behavior_expected": "answer",
  "behavior_actual": "answered",
  "behavior_ok": false,
  "cites_expected_passage": true,
  "all_claims_supported": true
}
```

## Human review

_Pending: open each cited slide and confirm it supports the claim._

<details><summary>Raw model output</summary>

```json
{
"claims": [
    {
        "text": "The 1958 Small Business Investment Act created the Small Business Investment Company program, which was a federal government licensing of private investment funds [1].",
        "citations": [1]
    },
    {
        "text": "The SBIC program leveraged low-cost government money, lending roughly $2–$3 for every $1 of private capital [1].",
        "citations": [1]
    },
    {
        "text": "This leveraging multiplied the early risk-capital pool and helped seed the Valley's first firms, such as Draper, Gaither & Anderson, in 1959 [1].",
        "citations": [1]
    }
],
"status": "answered","note": ""
}
```
</details>
