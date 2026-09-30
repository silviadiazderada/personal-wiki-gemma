# test-3: How did California's treatment of non-compete agreements shape Silicon Valley?

| | |
|---|---|
| Mode | ask · **local** execution |
| Model | `gemma4:e4b-it-qat` |
| Network during run | **online** |
| Retrieval | hybrid: bm25 + embeddinggemma:300m (RRF) (0.04s) |
| Model time | 7.87s |
| Memory | {"ollama_loaded": [{"model": "gemma4:e4b-it-qat", "size_gb": 3.1, "gpu_gb": 3.1}, {"model": "embeddinggemma:300m", "size_gb": 0.68, "gpu_gb": 0.68}], "ollama_process_rss_gb": 0.02, "system_used_gb": 14.43} |

## Expected (written before the run)

- Test type: connects two sources
- Expected behavior: `answered`
- Expected passages: `week-2-section:s15`, `week-5-section:s7`
- Expected answer: California does not enforce non-competes (a full ban since 2024), so engineers job-hop and ideas and talent cross-pollinate, making the Valley more dynamic than Boston's Route 128. The Week 5 midterm themes list this "labor rules" point as enabling talent mobility.

## Retrieved passages (what Gemma was shown)

**[1] Week 5 Section, slide 10** · `raw/POLECON156_Week5_DiscussionSection.pptx` · id `week-5-section:s10` · source  
<sub>rrf=0.0320, bm25 rank=1, embedding rank=4, cosine=0.47</sub>

> Practice essay questions
> Why did Silicon Valley emerge and endure? Choose three factors and show how they reinforce each other.
> Is the Silicon Valley story one of free markets alone? Use the role of the state in your answer.
> Compare Silicon Valley and Route 128. What explains the different outcomes?
> How do universities and immigration work together to build the region?
> How do networks shape who gets capital and opportunity?
> How did California's labor rules affect the region?

**[2] Week 2 Section, slide 15 (part 1)** · `raw/POLECON156_Week2_DiscussionSection.pptx` · id `week-2-section:s15` · source  
<sub>rrf=0.0313, bm25 rank=7, embedding rank=1, cosine=0.57</sub>

> Immigrants and the legal system
> THE LEGAL SYSTEM
> • Valley firms took equity instead of fees from cash-poor startups — the same risk mindset as a VC, and skin in the founder's game.
> • They built the scaffolding: incorporation, bylaws, hiring contracts, term sheets, M&A, IPOs. Wall Street firms couldn't adapt; Valley-native firms (Wilson Sonsini — Larry Sonsini, Cal grad) still dominate.
> • Conflict of interest is built in — the same firm may draft the term sheet for the investors across the table. “If there's no conflict, there's no interest.”
> • California won't enforce non-competes (full ban since 2024; still enforceable in New York) → engineers job-hop → ideas and talent cross-pollinate → more dynamic than Boston's Route 128.
> IMMIGRANTS
> • ~25% of US high-tech firms had an immigrant founder; ~40% of Valley firms by the internet era.
> • ~44% of Bay Area residents are foreign-born; ~38% of AI engineers are Chinese-born.
> • Berkeley and Stanford are the main talent pipelines; fully-funded STEM PhDs draw top talent on merit.
> • The vulnerability: tightening student visas and work authorization directly benefits China's AI sector.
> Closing question: does the Valley's reliance on immigrant founders make it stronger, or more vulnerable, as a global tech leader?

**[3] Week 5 Section, slide 7** · `raw/POLECON156_Week5_DiscussionSection.pptx` · id `week-5-section:s7` · source  
<sub>rrf=0.0308, bm25 rank=2, embedding rank=8, cosine=0.40</sub>

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

**[4] Week 2 Section, slide 5 (part 1)** · `raw/POLECON156_Week2_DiscussionSection.pptx` · id `week-2-section:s5` · source  
<sub>rrf=0.0308, bm25 rank=5, embedding rank=5, cosine=0.47</sub>

> The five pillars
> 1 · The state / government policy War and great-power competition have driven US innovation for 80 years. Federal and military money — WWII, the Cold War, Vannevar Bush's push for permanent research funding, Sputnik → NASA / ARPA / NDEA — built the foundation. In 1958, ~80% of Fairchild's business was government contracts.
> 2 · Research universities They supply the people. Stanford above all — Terman's applied-engineering culture, the Research Park, the faculty–student–industry loop — plus Berkeley, San José State, UCSF (biotech), Santa Clara (law).
> 3 · Venture capital Funding for ventures banks would never touch. Georges Doriot (1946), then the federal SBIC program (1958) that leveraged private risk capital, then the Valley's own firms from 1959. Decisive — but an insular network.
> 4 · Immigrants ~25% of US high-tech firms had an immigrant founder; ~40% of Valley firms by the internet era; ~44% of Bay Area residents are foreign-born. Berkeley and Stanford are the main pipelines.
> 5 · The legal system Valley law firms took equity instead of fees and built the scaffolding — incorporation, term sheets, M&A, IPOs. California's refusal to enforce non-competes keeps talent moving.
> Running through all five: a transversal counterculture / anti-establishment ethos (see later).

**[5] Week 2 Section, slide 2** · `raw/POLECON156_Week2_DiscussionSection.pptx` · id `week-2-section:s2` · source  
<sub>rrf=0.0298, bm25 rank=12, embedding rank=3, cosine=0.49</sub>

> What we covered this week
> We traced how the region emerged — from orchards to a federally funded research-and-defense economy.
> We put names to the story — the people who built the region and the institutions behind them.
> We mapped the unique factors that shaped Silicon Valley and why it’s difficult to find these somewhere else
> We examined Silicon Valley's less flattering side — structural inequality, the lack of diversity, self-reinforcing advantage, and the gap between the Valley's founding myths and its history.
> We connected the 1960s Bay Area counterculture to the birth of the personal computer.
> Speaker notes: Formal phrasing for the 'dark side': structural inequality / lack of diversity / self-reinforcing (vicious-cycle) advantage / myths and their paradoxes.

**[6] Week 2 Section, slide 6 (part 1)** · `raw/POLECON156_Week2_DiscussionSection.pptx` · id `week-2-section:s6` · source  
<sub>rrf=0.0295, bm25 rank=15, embedding rank=2, cosine=0.50</sub>

> How Silicon Valley emerged
> • Before the war it was orchards — the “Valley of Heart's Delight” — with a small radio-and-electronics cluster (Federal Telegraph; Hewlett-Packard, 1939).
> • World War II changed the scale. Vannevar Bush's Office of Scientific Research and Development poured federal money into university labs; Stanford's Fred Terman ran a wartime research lab and returned determined to tie Stanford to defense work.
> • The Cold War kept the money flowing — microwave, electronics, missiles. Lockheed Missiles & Space moved to Sunnyvale in 1956 and was the Valley's largest employer for decades.
> • Semiconductors spun out of that ecosystem: Shockley (1956) → Fairchild (1957) → Intel (1968). In 1958, ~80% of Fairchild's revenue came from government contracts.
> • Sputnik (1957) triggered another surge — NASA, ARPA, and the National Defense Education Act (1958): money for space, and for universities.
> • It was never insulated from politics or the business cycle. Defense budgets and the tech stock market rise and fall together — Washington shifts or a recession hits, the Valley lays off and grants dry up, then it booms on the next wave (chips → PCs → internet → AI). O'Mara calls this “boom and bust.”


## Gemma's answer

- California's refusal to enforce non-competes allowed talent mobility. [3]
- California's non-enforcement of non-competes enabled engineers to job-hop, which led to ideas and talent cross-pollinating, making the region more dynamic than Boston's Route 128. [2]
- Valley law firms took equity instead of fees and built the scaffolding for the industry, and California's refusal to enforce non-competes kept talent moving. [4]

## Citation checks (automatic)

| Claim | Cites | Numbers missing from cited text | Word overlap | Verdict |
|---|---|---|---|---|
| California's refusal to enforce non-competes allowed talent mobility.… | [3] | — | 0.62 | supported |
| California's non-enforcement of non-competes enabled engineers to job-hop, which led to id… | [2] | — | 0.65 | supported |
| Valley law firms took equity instead of fees and built the scaffolding for the industry, a… | [4] | — | 0.94 | supported |

## Automatic assessment

```json
{
  "retrieval_found_expected": true,
  "expected_passage_ranks": {
    "week-2-section:s15": 2,
    "week-5-section:s7": 3
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
"text": "California's refusal to enforce non-competes allowed talent mobility.",
"citations": [3]
},
{
"text": "California's non-enforcement of non-competes enabled engineers to job-hop, which led to ideas and talent cross-pollinating, making the region more dynamic than Boston's Route 128.",
"citations": [2]
},
{
"text": "Valley law firms took equity instead of fees and built the scaffolding for the industry, and California's refusal to enforce non-competes kept talent moving.",
"citations": [4]
}
],
"status": "answered","note": ""
}
```
</details>
