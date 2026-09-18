# Human annotation instructions

1. Open the lesson pack for the assigned lesson and annotate concepts, relations, grounding cases, and quiz decisions in the blank tables and CSV workbooks.
2. A concept is a meaningful teachable idea, method, process, algorithm, theory, object, or dependency—not every noun or repeated phrase.
3. A relation is valid only when the source text supports its direction and relation type. Co-occurrence or keyword overlap is insufficient.
4. Grounding uses `YES`, `PARTIAL`, or `NO`: direct support, partial support, or no support for the exact claim.
5. Quiz decisions use `GENERATE_QUIZ`, `DISAMBIGUATE`, or `REFUSE_UNGROUNDED`. Generate only when the source supports the question, answer, explanation, and citation.
6. Record uncertainty in `notes` and use `NEEDS_REVIEW` when a second reviewer is needed.
7. Any AI orientation summary or suggestion is labeled as non-ground-truth. Reviewer judgment overrides it.

Hypothetical example: “backpropagation updates weights using gradients” may be a concept/evidence candidate, but the reviewer must verify the exact page text before accepting it.
