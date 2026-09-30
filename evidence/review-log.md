# Review log

Each generated note was compared with the original slide it cites. Corrections were made in the wiki, never in `raw/`. Corrected notes carry `reviewed: true`, so re-ingestion will not overwrite them.

Reviewed on 2026-09-27 (model output from `gemma4:e4b-it-qat`). Snapshot before review: [`iterations/ingest-3-e4b-before-review/`](iterations/ingest-3-e4b-before-review/).

## Titles renamed with `wiki rename`

| Before | After | Why |
|---|---|---|
| Key Figures | Silicon Valley Pioneers | vague |
| Five Pillars | Five Pillars of Silicon Valley | not self-explanatory in the graph |
| Silicon Valley Emergence | Origins of Silicon Valley | awkward |
| Regional Models | Silicon Valley vs Route 128 | vague; moved Course → Concepts |
| Silicon Valley Themes | Midterm Themes | it is the Week 5 midterm theme list |
| Midterm Exam Logistics | Midterm Exam | shorter |
| Founder Interview Process | Founder Interview | shorter |
| Founder Outreach Strategy | Founder Outreach | shorter |
| Immigration in Silicon Valley | Immigrant Founders | clearer; moved Course → Concepts |

## Content corrections

| Note | Correction |
|---|---|
| [[Silicon Valley Pioneers]] | Fixed Shockley date error: slide 12 says 'Nobel 1956', the invention was not in 1956. Replaced vague summary. Added Felsenstein and Hardt-English from slide 12 and a link to Counterculture Ethos. |
| [[Counterculture Ethos]] | Fixed attribution error: slide 12 says Hardt-English LED Community Memory; Felsenstein was MC of Homebrew (the note said both created it). Sharpened the link reason. |
| [[Five Pillars of Silicon Valley]] | Rewrote a garbled fact (slide text had been run together). Named the five pillars in the summary. Added link to Stanford Research Park (universities pillar). |
| [[Origins of Silicon Valley]] | Removed LaTeX artifacts ($\rightarrow$) from the model output. Rewrote a vague link reason using the slide 6 speaker notes. |
| [[Venture Capital]] | Restored the key number the model dropped (slide 13: '$2–$3 ... for every $1'). Added link to Silicon Valley Pioneers (Doriot, Rock). |
| [[Immigrant Founders]] | Note was thin (one fact). Merged in the immigration facts from Week 2 slide 15 that the model had left inside Five Pillars. Replaced a loose link with two direct ones. |
| [[Legal System]] | Made the non-compete wording match slide 15 ('won't enforce', 'full ban since 2024'). Added the Route 128 link that slide 15 makes explicitly. |
| [[Silicon Valley vs Route 128]] | Summary now says what the subject is. Added the Week 2 slide 15 fact and a link to Legal System. |
| [[Midterm Themes]] | Replaced a loose link with direct links to Five Pillars and Midterm Exam. |

## Checked, no change needed

Stanford Research Park, Team Start-Up Competition, Startup Selection Rules, Startup Research Resources, Founder Interview, Founder Outreach, Midterm Exam, Professional Profile Building: facts match the cited slides (Week 3 slide numbers refer to the redacted file).

## Second pass (2026-09-29): after enriching the ingestion rules

Ingestion was changed to give people and named programs their own notes (21 → 32 notes). Snapshot before: [`iterations/ingest-4-before-enrichment/`](iterations/ingest-4-before-enrichment/).

Cleanup commands: `wiki rename "State Funding" "Government Funding"`, `wiki merge "Federal Government Role" "Government Funding"`, `wiki merge "Interview Question Development" "Founder Interview"`, `wiki rename "Online Retail Problem" "Jeff Bezos"`, `wiki rename "Pitchbook Usage" "Pitchbook"`.

| Note | Correction |
|---|---|
| [[Government Funding]] | Merged from 'State Funding' (Week 5) and 'Federal Government Role' (a Week 4 question-only topic). Rewrote the summary and the question-only fact; replaced link reasons that named the old note. |
| [[Vannevar Bush]] | Link reasons named the removed 'Federal Government Role' note or were loose; rewrote them from slide 6 and linked the Pioneers hub. |
| [[Sergey Brin and Larry Page]] | Summary said their motivations 'are questioned'; rewrote it to say what the source contains. Replaced a loose link to Origins of Silicon Valley. |
| [[Jeff Bezos]] | Renamed from 'Online Retail Problem'. Rewrote the summary; replaced a loose link to Founder Interview. |
| [[SBIC Program]] | Fact about the 1958 Small Business Investment Act cited slide 5, which does not mention the Act; corrected to slide 13. Added link to Venture Capital. |
| [[Non-Compete Agreements]] | First fact combined slide 5 with a 'cross-pollinate' detail that is only on slide 15; cited both. Tightened the summary. Added the Route 128 link from slide 15. |
| [[Janet Yellen]] | Tariff fact overstated the slide ('against China rather than unilateral tariffs'); now matches the quote about tariffs on allies. Link reason named the removed note. |
| [[Fred Terman]] | Checked against slides 6, 8 and 12: accurate. Added links to Pioneers and Vannevar Bush. |
| [[Silicon Valley Pioneers]] | Linked the new person notes (Vannevar Bush, Fred Terman) from the hub. |
