# Knowledge Base Setup Guide

This guide explains how to prepare a knowledge base for use with the `rag-legal-search` skill.

## Directory Structure

```
knowledge_base/
├── accounting_standards/
│   ├── ifrs_15_revenue.txt
│   ├── ias_36_impairment.txt
│   ├── ias_24_related_parties.txt
│   └── ifrs_9_financial_instruments.txt
├── audit_standards/
│   ├── isa_315_risk_assessment.txt
│   ├── isa_330_responses_to_risks.txt
│   └── isa_520_analytical_procedures.txt
└── company_policies/
    ├── revenue_recognition_policy.md
    └── expense_approval_policy.md
```

> Note: The skill reads only one directory level (non-recursive). Use a flat structure or run separate searches per subdirectory.

## Document Preparation Best Practices

### Chunking Strategy

The skill splits documents on `\n\n` (double newlines). To optimize retrieval:
- Separate each article, clause, or section with a blank line
- Keep each paragraph focused on one topic (50–300 words ideal)
- Avoid very long paragraphs — they reduce retrieval precision

### Content to Include

| Document Type          | Format | Notes                                    |
|------------------------|--------|------------------------------------------|
| IFRS/GAAP standards    | `.txt` | One standard per file                    |
| Chinese accounting standards (CAS) | `.txt` | Include standard number in filename |
| Internal audit manual  | `.md`  | One procedure per paragraph              |
| Regulatory circulars   | `.txt` | Strip cover page/signature blocks        |
| Past audit findings    | `.md`  | One finding per paragraph with keywords  |

### Naming Conventions

Use descriptive filenames since the filename appears in `citations.source`:

```
✅ ias_36_impairment_of_assets.txt
✅ audit_manual_chapter_3_sampling.md
❌ document1.txt
❌ scan.txt
```

## Updating the Knowledge Base

Simply add or modify `.txt`/`.md` files in the directory. The skill re-indexes on every call — no rebuild step required.

## Query Writing Tips

| Topic                       | Good Query                                          |
|-----------------------------|-----------------------------------------------------|
| Revenue recognition         | `"revenue recognition criteria performance obligation IFRS 15"` |
| Impairment                  | `"goodwill impairment testing cash generating unit"` |
| Related parties             | `"related party transaction disclosure requirements IAS 24"` |
| Going concern               | `"going concern indicators management assessment"`  |
