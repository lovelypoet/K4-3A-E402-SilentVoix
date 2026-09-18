# Real annotation guide

## Ground-truth rule

Human reviewers define the labels. Do not copy predictions from the AI system into these files. Annotate only evidence present in the cited source chunk.

## Concepts

Label a meaningful concept when it is a teachable idea, method, principle, process, important object, or meaningful relationship. Do not label speaker names, filenames, advertisements, incidental examples, or every noun. Aim for roughly 8–12 concepts per lesson, without forcing the count.

## Relations

Use only the controlled relation vocabulary in `spec.md` (currently including `prerequisite_of`, `used_for`, and `related_to` where explicitly supported). Include positive and invalid candidates. The source and target direction must be supported by the text; co-occurrence alone is not evidence.

## Grounding

Use `YES`, `PARTIAL`, or `NO`. Ask whether the exact source excerpt supports the claim. Same-lesson membership, topic similarity, or keyword overlap is not sufficient.

## Quiz decisions

Use `GENERATE_QUIZ` only when the evidence supports a question, answer, explanation, and citation. Use `DISAMBIGUATE` for competing or unclear interpretations. Use `REFUSE_UNGROUNDED` when evidence is absent or insufficient. Include supported, ambiguous, insufficient, unsupported, cross-concept, wrong-source, and adversarial cases across the five PDF lessons.

Review status should remain blank until a human reviews the row.
