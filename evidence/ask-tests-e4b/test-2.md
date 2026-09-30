# test-2: How did Stanford turn its real estate into an advantage for the tech industry?

| | |
|---|---|
| Mode | ask · **local** execution |
| Model | `gemma4:e4b-it-qat` |
| Network during run | **online** |
| Retrieval | hybrid: bm25 + embeddinggemma:300m (RRF) (1.097s) |
| Model time | 5.09s |
| Memory | {"ollama_loaded": [{"model": "gemma4:e4b-it-qat", "size_gb": 3.1, "gpu_gb": 3.1}, {"model": "embeddinggemma:300m", "size_gb": 0.68, "gpu_gb": 0.68}], "ollama_process_rss_gb": 0.02, "system_used_gb": 14.4} |

## Expected (written before the run)

- Test type: paraphrased (question says "real estate", slide says "land")
- Expected behavior: `answered`
- Expected passages: `week-2-section:s8`
- Expected answer: Stanford held land it was barred from selling, so Fred Terman leased it, creating Stanford Research Park (1951), the first university-owned industrial park. Firms next to campus recruited students, hired faculty as consultants, funded research and spun out of Stanford labs.

## Retrieved passages (what Gemma was shown)

**[1] Week 2 Section, slide 8** · `raw/POLECON156_Week2_DiscussionSection.pptx` · id `week-2-section:s8` · source  
<sub>rrf=0.0320, bm25 rank=4, embedding rank=1, cosine=0.66</sub>

> What made Stanford different
> • Land it could not sell. Stanford held a large endowment of land it was barred from selling; Fred Terman's answer was to lease it — creating Stanford Research Park (1951), the first university-owned industrial park.
> • Proximity became collaboration. Putting technology firms next to campus created a working loop: companies recruited students, hired faculty as consultants, funded research, and spun out of Stanford labs. Terman had already done this in miniature with Hewlett and Packard.
> • A deliberate tilt toward industry and the military. Terman moved the university's resources into science and engineering and built an applied-engineering culture explicitly to serve the military-industrial complex — where most universities kept industry at arm's length.
> Speaker notes: One cold call: 'What did Stanford do that a normal research university would not?' Answer: it fused the university with industry and the military on purpose.

**[2] Week 5 Section, slide 7** · `raw/POLECON156_Week5_DiscussionSection.pptx` · id `week-5-section:s7` · source  
<sub>rrf=0.0313, bm25 rank=3, embedding rank=5, cosine=0.40</sub>

> Big themes from the readings
> Immigration
> Universities draw global talent. Many students intern, get hired and stay.
> The state
> Government funded foundational tech (DARPA, ARPANET, GPS). Mazzucato's argument.
> Labor rules
> California's non-enforcement of non-competes enabled talent mobility.
> Networks & capital
> Tight networks and VC clustering near Stanford. Each generation funds the next.
> Regional model
> Saxenian: Silicon Valley (open, networked) vs. Route 128 (hierarchical, insular).
> Universities
> Stanford and Berkeley: proximity to faculty, peers and industry.

**[3] Week 2 Section, slide 5 (part 1)** · `raw/POLECON156_Week2_DiscussionSection.pptx` · id `week-2-section:s5` · source  
<sub>rrf=0.0311, bm25 rank=7, embedding rank=2, cosine=0.43</sub>

> The five pillars
> 1 · The state / government policy War and great-power competition have driven US innovation for 80 years. Federal and military money — WWII, the Cold War, Vannevar Bush's push for permanent research funding, Sputnik → NASA / ARPA / NDEA — built the foundation. In 1958, ~80% of Fairchild's business was government contracts.
> 2 · Research universities They supply the people. Stanford above all — Terman's applied-engineering culture, the Research Park, the faculty–student–industry loop — plus Berkeley, San José State, UCSF (biotech), Santa Clara (law).
> 3 · Venture capital Funding for ventures banks would never touch. Georges Doriot (1946), then the federal SBIC program (1958) that leveraged private risk capital, then the Valley's own firms from 1959. Decisive — but an insular network.
> 4 · Immigrants ~25% of US high-tech firms had an immigrant founder; ~40% of Valley firms by the internet era; ~44% of Bay Area residents are foreign-born. Berkeley and Stanford are the main pipelines.
> 5 · The legal system Valley law firms took equity instead of fees and built the scaffolding — incorporation, term sheets, M&A, IPOs. California's refusal to enforce non-competes keeps talent moving.
> Running through all five: a transversal counterculture / anti-establishment ethos (see later).

**[4] Week 2 Section, slide 2** · `raw/POLECON156_Week2_DiscussionSection.pptx` · id `week-2-section:s2` · source  
<sub>rrf=0.0308, bm25 rank=2, embedding rank=8, cosine=0.38</sub>

> What we covered this week
> We traced how the region emerged — from orchards to a federally funded research-and-defense economy.
> We put names to the story — the people who built the region and the institutions behind them.
> We mapped the unique factors that shaped Silicon Valley and why it’s difficult to find these somewhere else
> We examined Silicon Valley's less flattering side — structural inequality, the lack of diversity, self-reinforcing advantage, and the gap between the Valley's founding myths and its history.
> We connected the 1960s Bay Area counterculture to the birth of the personal computer.
> Speaker notes: Formal phrasing for the 'dark side': structural inequality / lack of diversity / self-reinforcing (vicious-cycle) advantage / myths and their paradoxes.

**[5] Week 2 Section, slide 7** · `raw/POLECON156_Week2_DiscussionSection.pptx` · id `week-2-section:s7` · source  
<sub>rrf=0.0292, bm25 rank=11, embedding rank=6, cosine=0.40</sub>

> What did Stanford do that an ordinary research university would not?
> One answer each — then we'll piece it together.

**[6] Week 2 Section, slide 6 (part 1)** · `raw/POLECON156_Week2_DiscussionSection.pptx` · id `week-2-section:s6` · source  
<sub>rrf=0.0290, bm25 rank=16, embedding rank=3, cosine=0.42</sub>

> How Silicon Valley emerged
> • Before the war it was orchards — the “Valley of Heart's Delight” — with a small radio-and-electronics cluster (Federal Telegraph; Hewlett-Packard, 1939).
> • World War II changed the scale. Vannevar Bush's Office of Scientific Research and Development poured federal money into university labs; Stanford's Fred Terman ran a wartime research lab and returned determined to tie Stanford to defense work.
> • The Cold War kept the money flowing — microwave, electronics, missiles. Lockheed Missiles & Space moved to Sunnyvale in 1956 and was the Valley's largest employer for decades.
> • Semiconductors spun out of that ecosystem: Shockley (1956) → Fairchild (1957) → Intel (1968). In 1958, ~80% of Fairchild's revenue came from government contracts.
> • Sputnik (1957) triggered another surge — NASA, ARPA, and the National Defense Education Act (1958): money for space, and for universities.
> • It was never insulated from politics or the business cycle. Defense budgets and the tech stock market rise and fall together — Washington shifts or a recession hits, the Valley lays off and grants dry up, then it booms on the next wave (chips → PCs → internet → AI). O'Mara calls this “boom and bust.”


## Gemma's answer

- Stanford held a large endowment of land that it was barred from selling, so Fred Terman leased it to create Stanford Research Park in 1951, which was the first university-owned industrial park. [1]

## Citation checks (automatic)

| Claim | Cites | Numbers missing from cited text | Word overlap | Verdict |
|---|---|---|---|---|
| Stanford held a large endowment of land that it was barred from selling, so Fred Terman le… | [1] | — | 0.89 | supported |

## Automatic assessment

```json
{
  "retrieval_found_expected": true,
  "expected_passage_ranks": {
    "week-2-section:s8": 1
  },
  "behavior_expected": "answered",
  "behavior_actual": "answered",
  "behavior_ok": true,
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
"text": "Stanford held a large endowment of land that it was barred from selling, so Fred Terman leased it to create Stanford Research Park in 1951, which was the first university-owned industrial park [1].",
"citations": [1]
}
],
"status": "answered","note": ""
}
```
</details>
