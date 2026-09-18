# Fine-tuning Decision

**Recommendation: MORE REAL DATA REQUIRED BEFORE DECISION.**

Iteration 1 uses 26 corrected synthetic cases and zero human-rated quizzes. The decision layer reached 1.000 accuracy with zero false `GENERATE_QUIZ`, but only 10 generated quizzes were publishable after deterministic semantic validation; five outputs were withheld. Citation accuracy is 0.692 because withheld outputs have no final citation, and the quality bar remains unmet.

The strongest components are concept extraction and relation extraction at F1 1.000. The remaining bottleneck is claim-level quiz grounding and semantic validation. No failure meets the strict `MODEL_CAPABILITY` definition because deterministic policy/validator behavior explains the observed cases.

The real corpus has no human-labeled gold cases. One provisional lesson is marked for annotation; other candidates are excluded for duplicate source groups, encoding corruption, missing IDs, zero chunks, or low-information extraction. Fine-tuning cannot be justified until 5-10 clean source-group-separated lessons and 30-60 human-reviewed quiz cases are available.

Next experiment: repair/re-ingest the real corpus, add lecturer labels, run separate real metrics, then compare prompt, retrieval, policy, and validator fixes before considering any specific module for fine-tuning.
