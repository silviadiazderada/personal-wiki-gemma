# test-4: What was the U.S. capital gains tax rate in 1990?

| | |
|---|---|
| Mode | ask · **local** execution |
| Model | `gemma4:e4b-it-qat` |
| Network during run | **offline** |
| Retrieval | hybrid: bm25 + embeddinggemma:300m (RRF) (0.041s) |
| Model time | 10.08s |
| Memory | {"ollama_loaded": [{"model": "gemma4:e4b-it-qat", "size_gb": 5.55, "gpu_gb": 5.55}, {"model": "embeddinggemma:300m", "size_gb": 0.68, "gpu_gb": 0.68}], "ollama_process_rss_gb": 0.02, "system_used_gb": 14.73} |

## Expected (written before the run)

- Test type: unsupported (not in the wiki)
- Expected behavior: `insufficient_evidence`
- Expected passages: none
- Expected answer: No source mentions capital gains tax rates. The correct response is an explicit statement that the wiki does not contain this information, with no guessed number.

## Retrieved passages (what Gemma was shown)

**[1] Week 2 Section, slide 16** · `raw/POLECON156_Week2_DiscussionSection.pptx` · id `week-2-section:s16` · source  
<sub>rrf=0.0320, bm25 rank=1, embedding rank=4, cosine=0.14</sub>

> JANET YELLEN AT BERKELEY · “LEADING AT THE EDGE” · SEPT 2, 2026
> Berkeley Haas professor emerita (1980–94); Chair of the Federal Reserve, then U.S. Treasury Secretary. Her whole career is about the state's role in the economy
> “A job isn't just a paycheck — it's self-respect. My aim has always been an economy where people feel secure that they can find work and keep it.”
> “Put tariffs on our allies and it makes little sense — but if the US and Europe act together, we have real leverage against China.”
> Speaker notes: 3 photo slots. Context line ties her to pillar 1. Gloss #1: employment as dignity, rooted in her father's Depression-era patients; AI already cutting entry-level hiring. Gloss #2: wary of tariffs (raise prices, hit allies); prefers US+Europe coordination + industrial policy.

**[2] Week 2 Section, slide 13 (part 1)** · `raw/POLECON156_Week2_DiscussionSection.pptx` · id `week-2-section:s13` · source  
<sub>rrf=0.0320, bm25 rank=3, embedding rank=2, cosine=0.15</sub>

> Venture capital — why it mattered, and why it stayed closed
> • It financed the un-financeable. A bank wants collateral and steady repayment; a startup has neither. Venture capital put in equity, took a board seat, and absorbed the loss when a company failed — which made funding high-risk ventures possible at all.
> • The government primed the pump — the SBIC. The 1958 Small Business Investment Act created the Small Business Investment Company program: the federal government licensed private investment funds and leveraged them, lending roughly $2–$3 of low-cost government money for every $1 of private capital. It multiplied the early risk-capital pool and seeded the Valley's first firms (Draper, Gaither & Anderson, 1959).
> • But it became a closed circle. Venture capital is still an insular “old-boys network.” Many partners are former founders who back people like themselves; talent is evenly distributed, opportunity is not. Some rise in East and South Asian representation — very few Latino or Black investors. Who hears about a deal, and who gets the introduction, still favors insiders.
> John Doerr, on “pattern recognition” (O'Mara, p. 75): backing “white male nerds who dropped out of Harvard or Stanford and have no social life.”

**[3] Week 3 Section, slide 2** · `raw/POLECON156_Week3_DiscussionSection.pptx` · id `week-3-section:s2` · source  
<sub>rrf=0.0315, bm25 rank=2, embedding rank=5, cosine=0.12</sub>

> Written reflection
> TODAY'S PROMPT
> 1. Why was Japan's rise in the electronics industry a “wake-up call” for Silicon Valley in the 1980s?
> 2. How did the U.S. government respond — and was its response protectionism, industrial policy, or both?
> Instructions
> • 7 minutes (+2 to upload)
> • Handwritten in your spiral notebook — no devices, open-book (The Code + Course Reader OK).
> • A short paragraph per question — the whole reflection on ONE page.
> • Take a screenshot and upload it to bCourses under Week 3 Reflection.
> Speaker notes: Graded randomly, 4 pts (2 quality, 2 thoughtfulness). Q1 target: VLSI standardized chip design and split design from manufacturing, so MITI-backed Japanese firms could learn the process and compete. Q2 targets: SEMATECH (DARPA + 14 chip firms), DARPA's $1B Strategic Computing Initiative, the 1986 US–Japan Semiconductor Agreement. China parallel: CHIPS Act + export controls — keep it factual, not partisan.

**[4] Week 2 Section, slide 5 (part 1)** · `raw/POLECON156_Week2_DiscussionSection.pptx` · id `week-2-section:s5` · source  
<sub>rrf=0.0313, bm25 rank=7, embedding rank=1, cosine=0.16</sub>

> The five pillars
> 1 · The state / government policy War and great-power competition have driven US innovation for 80 years. Federal and military money — WWII, the Cold War, Vannevar Bush's push for permanent research funding, Sputnik → NASA / ARPA / NDEA — built the foundation. In 1958, ~80% of Fairchild's business was government contracts.
> 2 · Research universities They supply the people. Stanford above all — Terman's applied-engineering culture, the Research Park, the faculty–student–industry loop — plus Berkeley, San José State, UCSF (biotech), Santa Clara (law).
> 3 · Venture capital Funding for ventures banks would never touch. Georges Doriot (1946), then the federal SBIC program (1958) that leveraged private risk capital, then the Valley's own firms from 1959. Decisive — but an insular network.
> 4 · Immigrants ~25% of US high-tech firms had an immigrant founder; ~40% of Valley firms by the internet era; ~44% of Bay Area residents are foreign-born. Berkeley and Stanford are the main pipelines.
> 5 · The legal system Valley law firms took equity instead of fees and built the scaffolding — incorporation, term sheets, M&A, IPOs. California's refusal to enforce non-competes keeps talent moving.
> Running through all five: a transversal counterculture / anti-establishment ethos (see later).

**[5] Week 2 Section, slide 13 (part 2)** · `raw/POLECON156_Week2_DiscussionSection.pptx` · id `week-2-section:s13.2` · source  
<sub>rrf=0.0291, bm25 rank=4, embedding rank=14, cosine=0.09</sub>

> Venture capital — why it mattered, and why it stayed closed
> Speaker notes: Fund structure and the 'good VC' checklist are deliberately left out. Focus: why VC exists, the SBIC as government scaffolding, the diversity problem.

**[6] Week 2 Section, slide 3** · `raw/POLECON156_Week2_DiscussionSection.pptx` · id `week-2-section:s3` · source  
<sub>rrf=0.0291, bm25 rank=5, embedding rank=13, cosine=0.09</sub>

> Today
> • 01 · The five pillars that made Silicon Valley — and keep it competitive
> • 02 · How the Valley emerged, and what made Stanford different
> • 03 · Written reflection
> • 04 · Who is this? — Poll Everywhere activity
> • 05 · Venture capital: why it mattered, and why it stayed closed
> • 06 · The counterculture thread · immigrants and the legal system · Janet Yellen


## Gemma's answer

**Insufficient evidence.** The wiki does not contain information about the U.S. capital gains tax rate in 1990.

## Citation checks (automatic)

| Claim | Cites | Numbers missing from cited text | Word overlap | Verdict |
|---|---|---|---|---|

## Automatic assessment

```json
{
  "retrieval_found_expected": null,
  "expected_passage_ranks": {},
  "behavior_expected": "insufficient_evidence",
  "behavior_actual": "insufficient_evidence",
  "behavior_ok": true,
  "cites_expected_passage": null,
  "all_claims_supported": null
}
```

## Human review

_Pending: open each cited slide and confirm it supports the claim._

<details><summary>Raw model output</summary>

```json
{
"claims": [],
"status": "insufficient_evidence",
"note": "The wiki does not contain information about the U.S. capital gains tax rate in 1990."
}
```
</details>
