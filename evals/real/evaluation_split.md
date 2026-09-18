# Real evaluation split and anti-overfitting protocol

This split is frozen before human labeling.

## `real_dev` — annotation/development set

The five currently selected lessons are used for the first human annotation round:

- `lesson_05`
- `lesson_55`
- `lesson_57`
- `lesson_59`
- `lesson_60`

These labels may be used to inspect errors and develop changes to prompts, retrieval, policy, validators, or presentation. Any development metrics must be reported as `real_dev` metrics only.

## `real_test` — held-out set

The remaining candidates are reserved for final evaluation:

- `lesson_56`
- `lesson_58`

They must not be used to tune prompts, validators, policies, retrieval, or model weights before the final held-out report. Their source groups remain isolated from `real_dev`.

## Required reporting order

1. Freeze the split and human labels.
2. Develop only against `real_dev`, recording changes and stopping criteria.
3. Freeze the implementation.
4. Run predictions once on `real_test`.
5. Report `real_dev` and `real_test` separately; never combine them into one final number.

If the held-out set is too small for a reliable claim, report that limitation rather than reusing it for tuning.
