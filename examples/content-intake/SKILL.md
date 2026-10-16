---
name: thinklab-curated-intake
description: Collect a small, original, reviewed batch for the local ThinkLab library and daily plan.
---

Use the user's existing external scheduler; do not create OS tasks or change Codex automations.

1. Inspect the local catalog and complete lesson IDs first. Select at most ten relevant problems, normally two. Do not scrape an entire library or copy third-party solutions. Author teaching and references yourself and keep official exercise permalinks.
2. For complete lessons, generate a schemaVersion 1 digest-bound manifest with `python scripts/export_reference_batch.py --day YYYY-MM-DD --batch-id curated-YYYY-MM-DD ID ID`. Preserve the output as UTF-8 JSON.
3. New lessons use `{id, candidate:{rights:"original",lesson:{...},solutions:{csharp,python,java,javascript,typescript}}}`. Follow docs/content-spec.md and docs/content-integration.md exactly. Select an already shipped trace with matching semantics/examples. New executable trace code needs ordinary source review outside intake.
4. Run `python scripts/import_batch.py batch.json` for a read-only local preflight. A valid candidate is pending review, not published or planned.
5. If the local-machine endpoint was explicitly enabled by its owner, `python scripts/import_batch.py batch.json --apply --host HOST` stages new candidates privately. It never executes incoming code. If disabled, report that fact; do not change network settings, credentials or automation configuration.
6. Only the trusted local maintainer may approve a digest-bound review after actual rights/semantic, independent trace oracle, five-language and UI tests. See the review template and `scripts/publish_reviewed_batch.py`. Do not self-assert test success from payload claims. The HTTP API cannot publish candidates.
7. After publication, resubmit the unchanged batch. Intake verifies each ID/content digest, then reuses the existing daily-plan merge. Repeats retain order, revisions and all learning state. Never mark a lesson done on the user's behalf.
8. Report success only after confirmed API response and plan refresh. Preserve batch ID and day on retries. Conflicts require reviewing the current source; never overwrite it or switch the batch ID just to bypass a conflict.
