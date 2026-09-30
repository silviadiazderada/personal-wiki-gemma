# Re-ingestion after cleanup (renames + review)

Forcing Gemma to re-read Week 5 Section, whose notes were renamed from Regional Models, Silicon Valley Themes, Midterm Exam Logistics and Immigration in Silicon Valley.

```
model: gemma4:e4b-it-qat · execution: local · network: online
  → Week 5 Section: 12 passages, asking gemma4:e4b-it-qat for topics…
                                Ingestion report                                
┌─────────────────┬────────────────────────────────────────────────────────────┐
│ sources         │ week-5-section                                             │
│ skipped_sources │ —                                                          │
│ created         │ —                                                          │
│ updated         │ Midterm Exam, Professional Profile Building, Midterm       │
│                 │ Themes, Immigrant Founders, Silicon Valley vs Route 128    │
│ merged          │ —                                                          │
│ removed         │ —                                                          │
│ kept_reviewed   │ Venture Capital, Counterculture Ethos, Legal System,       │
│                 │ Silicon Valley Pioneers, Five Pillars of Silicon Valley,   │
│                 │ Origins of Silicon Valley, Silicon Valley vs Route 128,    │
│                 │ Midterm Themes, Immigrant Founders                         │
│ rejected_titles │ —                                                          │
│ notes in wiki   │ 17                                                         │
│ files written   │ 1                                                          │
│ index           │ 47 source passages + 21 wiki notes (embeddings:            │
│                 │ embeddinggemma:300m)                                       │
│ time            │ 45.2s total, 30.2s in the model                            │
└─────────────────┴────────────────────────────────────────────────────────────┘
```
same file list before and after: yes
