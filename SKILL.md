---
name: seedance-25-prompt-reviewer
description: Review and minimally revise existing Seedance 2.5 video prompts while preserving locked plot, dialogue, characters, wardrobe, timing, and reference tags; conditionally check version-specific duration handling, continuity, speaker framing, lip-sync, over-shoulder, reverse-shot, OS, and VO logic. Use for optimizing or troubleshooting an existing Seedance 2.5 prompt, especially requests such as “只改画面/其他内容保持不变” or reports of character, camera, dialogue, or staging errors. Not a general from-scratch video ideation template.
license: MIT
---

# Seedance 25 Prompt Reviewer

Optimize and quality-check a prompt the user already wrote. Preserve the user's creative decisions; do not turn prompt repair into a new concept.

## Scope and authority

- Work in `review-only`, `ordinary revision`, or `minimal-difference revision` mode. Infer the narrowest mode that satisfies the request.
- User-locked content outranks this skill's creative defaults. Never silently change plot, exact dialogue, character labels, wardrobe, props, scene, timestamps, total duration, aspect ratio, or reference tags.
- Treat references and tags as contracts. Preserve every user-supplied tag byte-for-byte; do not translate, normalize, recase, respell, or renumber it.
- Prompt revision authorizes text work only. Do not upload assets, generate video, spend credits, or claim to have viewed an output without separate authorization and actual inspection.
- Separate internal consistency from model performance. A clean prompt is not proof of a successful Seedance 2.5 render.

## Route only what is needed

1. For any revision, read [prompt-revision.md](references/prompt-revision.md).
2. Read [seedance-25-adapter.md](references/seedance-25-adapter.md) when version, duration, material limits, extension, editing, real-person material, API fields, model IDs, or platform capability affects the answer. Do not borrow numeric or platform-specific limits from Seedance 2.0.
3. Read [continuity-check.md](references/continuity-check.md) when the prompt has multiple time ranges, shots, characters, wardrobe or prop states, spatial directions, lighting phases, or continuation boundaries.
4. Read [dialogue-staging.md](references/dialogue-staging.md) only when at least one full-check trigger below is present. For OS/VO/telephone/broadcast-only dialogue, perform the lightweight label check described below without loading the full staging module.
5. Read [source-notes.md](references/source-notes.md) only when making platform claims, resolving conflicting upstream guidance, or explaining provenance and evidence level.

### Full dialogue-staging triggers

Load the full module when any condition is true:

- two or more visible characters share a scene with explicit dialogue;
- the speaker changes between adjacent time ranges;
- the prompt uses over-shoulder, reverse shot, foreground back/shoulder, eyeline, confrontation, question-and-answer, or equivalent staging;
- the user reports a wrong speaker, wrong lip movement, front/back reversal, or position error.

Do not force a reverse-shot rewrite for a silent action scene, single-person monologue or presenter, clearly marked narration/VO/OS/telephone/broadcast audio, product/scenery/VFX shot, a user-locked wide two-shot, or an already unambiguous composition that does not request shot/reverse-shot coverage. A fixed wide two-shot may still need a speaker/lip-silence check; respect the composition.

For any off-screen line, check that the speaker is actually marked `OS` (or an unambiguous equivalent). `VO` and narration do not require the speaker's face.

## Revision workflow

1. Extract the user's requested change and a lock ledger before editing. If they say “只修改画面” or “其他内容保持不变”, everything outside the named span is locked verbatim.
2. Diagnose conflicts without rewriting yet. Distinguish `确定冲突`, `需要人工判断`, and `未触发此检查器`.
3. Apply the smallest sufficient change. Keep exact dialogue, timing, names, labels, and tags unless the user explicitly unlocked them.
4. Recheck old-state residue, mutually exclusive actions, uncovered time, reference-tag drift, continuity endpoints, and conditional dialogue staging.
5. For a revision, return one complete copy-ready replacement prompt by default, not only a patch. Briefly list what changed and what was held fixed. For review-only work, report issues without rewriting.

When deterministic support is useful, encode the internally extracted staging facts as JSON and run `scripts/prompt_review_checks.py`. The script validates a semantic ledger; it does not extract film meaning from raw prose and must not be presented as doing so.

## Output discipline

- Preserve the user's language and exact quoted dialogue.
- Prefer observable subject, action, scene, camera, motivated light, sound, and endpoint language over empty quality adjectives.
- If facts are uncertain, retain the source's evidence label and verification date. Never convert a third-party report or untested hypothesis into an official guarantee.
- State the validation boundary: `提示词内部一致性已检查；实际生成效果未验证` unless an actual generated video was inspected.
