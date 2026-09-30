## 1. Re-run ingest on all sources (unchanged files)
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
│ notes in wiki   │ 18                                                         │
│ files written   │ 0                                                          │
│ index           │ 47 source passages + 22 wiki notes (embeddings:            │
│                 │ embeddinggemma:300m)                                       │
│ time            │ 1.5s total, 0.0s in the model                              │
└─────────────────┴────────────────────────────────────────────────────────────┘
```
## 2. Force the model to re-read Week 2 Section
```
model: gemma4:e4b-it-qat · execution: local · network: online
  → Week 2 Section: 23 passages, asking gemma4:e4b-it-qat for topics…
                                Ingestion report                                
┌─────────────────┬────────────────────────────────────────────────────────────┐
│ sources         │ week-2-section                                             │
│ skipped_sources │ —                                                          │
│ created         │ —                                                          │
│ updated         │ Five Pillars, Silicon Valley Emergence, Stanford Research  │
│                 │ Park, Venture Capital, Immigrant Founders, Labor Rules,    │
│                 │ Counterculture Ethos                                       │
│ merged          │ Legal System → Labor Rules                                 │
│ removed         │ Fred Terman, Non-Compete Agreements                        │
│ kept_reviewed   │ —                                                          │
│ rejected_titles │ —                                                          │
│ notes in wiki   │ 16                                                         │
│ files written   │ 8                                                          │
│ index           │ 47 source passages + 20 wiki notes (embeddings:            │
│                 │ embeddinggemma:300m)                                       │
│ time            │ 130.5s total, 83.5s in the model                           │
└─────────────────┴────────────────────────────────────────────────────────────┘
```
