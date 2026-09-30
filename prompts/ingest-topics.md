# Ingestion rules: source -> wiki topics

You turn one course source (numbered slides) into topics for an Obsidian wiki about POLECON 156: Silicon Valley & the Global Economy.

Rules:
1. Pick 5 to 12 distinct subjects that the slides explain with facts: people, concepts, organizations, policies or events, or course logistics (assignments, project rules, exams).
2. Prefer specific subjects over umbrella topics. Every person with their own description on a slide gets their own People note (e.g. "Fred Terman", "Arthur Rock", "Mario Savio"). A named program, law, company or event with its own facts gets its own note (e.g. "SBIC Program", "Non-Compete Agreements", "Stanford Research Park"). Skip subjects that only appear as a question with no information. If the source only contains questions, return the 1 or 2 subjects it is about, with facts describing what the prompt asks.
3. `title`: the plain name of the subject in 1 to 4 words, the way an encyclopedia names an entry.
   Good: "Venture Capital", "Stanford Research Park", "Fred Terman", "Non-Compete Agreements", "SBIC Program", "Founder Interview", "Midterm Exam".
   Bad: "Venture Capital Role", "Stanford Research Park Model", "Legal System Impact", "Silicon Valley Emergence History", "Key Figures", "Startup Selection Criteria Overview". Do not add words like Role, Model, Impact, History, Overview, Structure, Criteria, Steps, Strategy, Motivation.
4. `summary`: 1 to 2 sentences that start with the subject and say what it is, e.g. "Stanford Research Park is ...". Never start with "This topic" or "This subject".
5. `facts`: 1 to 5 short factual statements taken from the slides, each with the slide numbers that support it. Copy numbers, names and dates exactly. No outside knowledge.
6. `source_summary`: 2 sentences describing what the whole source covers.
