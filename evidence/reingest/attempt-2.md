# Re-ingestion check

Notes before: 21

## 1. Re-run ingest on all sources (files unchanged)
```
model: gemma4:e4b-it-qat · execution: local · network: online
  = Week 2 Section: unchanged since last ingest, skipping the model
  = Week 3 Section: unchanged since last ingest, skipping the model
  = Week 4 Reflection: unchanged since last ingest, skipping the model
  = Week 5 Section: unchanged since last ingest, skipping the model
                                Ingestion report                                
┌─────────────────┬────────────────────────────────────────────────────────────┐
│ sources         │ week-2-section, week-3-section, week-4-reflection,         │
│                 │ week-5-section                                             │
│ skipped_sources │ week-2-section, week-3-section, week-4-reflection,         │
│                 │ week-5-section                                             │
│ created         │ —                                                          │
│ updated         │ —                                                          │
│ merged          │ —                                                          │
│ removed         │ —                                                          │
│ kept_reviewed   │ —                                                          │
│ rejected_titles │ —                                                          │
│ notes in wiki   │ 17                                                         │
│ files written   │ 0                                                          │
│ index           │ 47 source passages + 21 wiki notes (embeddings:            │
│                 │ embeddinggemma:300m)                                       │
│ time            │ 1.6s total, 0.0s in the model                              │
└─────────────────┴────────────────────────────────────────────────────────────┘
```
## 2. Force Gemma to re-read Week 2 Section
```
model: gemma4:e4b-it-qat · execution: local · network: online
  → Week 2 Section: 23 passages, asking gemma4:e4b-it-qat for topics…
                                Ingestion report                                
┌─────────────────┬────────────────────────────────────────────────────────────┐
│ sources         │ week-2-section                                             │
│ skipped_sources │ —                                                          │
│ created         │ —                                                          │
│ updated         │ Five Pillars, Silicon Valley Emergence, Stanford Research  │
│                 │ Park, Venture Capital, Counterculture Ethos, Legal System, │
│                 │ Key Figures                                                │
│ merged          │ —                                                          │
│ removed         │ —                                                          │
│ kept_reviewed   │ —                                                          │
│ rejected_titles │ —                                                          │
│ notes in wiki   │ 17                                                         │
│ files written   │ 0                                                          │
│ index           │ 47 source passages + 21 wiki notes (embeddings:            │
│                 │ embeddinggemma:300m)                                       │
│ time            │ 135.5s total, 99.2s in the model                           │
└─────────────────┴────────────────────────────────────────────────────────────┘
```
