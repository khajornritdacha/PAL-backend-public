# Evaluation archive

Artifacts behind the evaluation in:

> V. Khajornritdacha, K. Charojrochkul, K. Maneesri, T. Wong-Asa, P. Punyabukkana, and A. Suchato,
> "An Asynchronous Microservice Architecture for LLM-Driven Generation of Narrated Instructional
> Slides in Personalized Adaptive Learning," in *Proc. 10th Int. Conf. on Information Technology
> (InCIT 2026)*, Bangkok, Thailand, 2026.

The study compares two iterations of the pipeline on seven lessons: **V1**, the earlier pipeline, and
**V2**, the pipeline described in the paper. Each deck and its narration were scored three times by
one LLM judge (Claude Sonnet 4.6) using a rubric grounded in Mayer's Cognitive Theory of Multimedia
Learning (CTML).

## Layout

```
evaluation/
├── README.md
├── rubric.txt                 # judge rubric: 6 CTML principles × 5 criteria, 0–2 each
├── per-lesson-scores.csv      # 42 rows: lesson × condition × run × six dimensions
├── reproduce_table2.py        # recomputes Table II and the Section V.B statistics
└── lessons/
    └── NN_Topic/
        ├── goal.txt               # learner goal document, the only pipeline input (02–07)
        ├── outline.json           # course outline generated from the goal
        ├── generation_log.json    # V2 generation record: markdown, per-slide EN/TH narration, sections
        ├── judge_prompt.txt       # full prompt sent to the judge for this lesson
        ├── v1/
        │   ├── slides.pdf  slides.pptx
        │   ├── transcript.json    # per-slide narration
        │   └── score1.json  score2.json  score3.json
        └── v2/
            └── (same files as v1)
```

Each `scoreN.json` holds one judge run. For every principle it records five criterion scores (0–2),
the principle total (0–10), the effect-size weight `d_weight`, and the judge's written evidence.

| Lesson | Domain |
|---|---|
| 01_LearningTheory | Education: learning theories |
| 02_Climate | Earth science: climate change |
| 03_IPLaw | Law: intellectual property |
| 04_ColdWar | History: the Cold War |
| 05_Nutrient | Health science: nutrition and metabolism |
| 06_ConsumerBehaviour | Business: consumer behaviour |
| 07_Finance | Finance: financial statements and ratio analysis |

## Reproducing the reported numbers

```sh
pip install numpy scipy
python reproduce_table2.py
```

The script reads the raw `scoreN.json` files, not the CSV. It prints:

- every Table II row (mean ± SD across lessons, delta, per-lesson range, lessons improved)
- the exact two-sided Wilcoxon test
- both sensitivity composites
- the judge's run-to-run consistency (ICC(1,1), mean range, agreement within one point)

## Regenerating decks

The generation pipeline is the code in this repository. See the root `README.md` to start the services
and the n8n workflows in `../workflows/`, which contain the generation prompts. To regenerate a
lesson, create a course from its `goal.txt`. No reference documents were uploaded for any of the
seven lessons. LLM outputs are not deterministic, so a regenerated deck will not match the archived
one exactly. The archived decks are the ones that were scored.

The RAG path needs a MongoDB Atlas vector search index named `vector_index` on the `rag` collection
(3072-dimension `gemini-embedding-001` embeddings). This did not affect the evaluation, because no
source documents were uploaded.

## Notes

- **Lesson 01 has no `goal.txt`.** The original goal document was not kept. The learner's goal
  statement survives in the `goal` field of `lessons/01_LearningTheory/outline.json`, but the
  surrounding context that the other goal documents contain does not.
- **Scoring was in English only.** V2 generates English and Thai narration, and
  `generation_log.json` keeps both. Only the English narration (`transcript.json`) was scored.
- **Account identifiers are redacted.** `userId` and `mentorId` in each `outline.json` are
  `REDACTED`. The mentor notes and learner goals were written for this evaluation and are not
  real student data.
- **Only V1 and V2 are included here.** Comparisons with other tools are out of scope for this archive.

## License

Released under the repository's MIT License (see `../LICENSE`).
