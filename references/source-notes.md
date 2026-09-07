# Sources, attribution, and evidence boundary

This skill is an original review-focused adaptation. It does not copy either upstream repository wholesale.

## Upstream A: creative and review core

- Repository: https://github.com/Emily2040/seedance-2.0
- Reviewed commit: `39f3543a5d23ee3720e5bdd5a57172e0fa6c464a`
- Reviewed: 2026-09-07
- License: MIT, copyright 2026 Iamemily2050 (@iamemily2050)

Adapted decision-changing ideas:

- user intent and reference contracts outrank style defaults;
- one motivated camera move, physically motivated light, observable action, and explicit endpoint;
- action chain from initial state through follow-through;
- exact preservation of reference tags and separation of asset responsibilities;
- continuity ledger for identity, wardrobe, props, space, light, camera, action, and sound;
- anti-slop replacement of empty quality language with observable production choices;
- retake/rewrite diagnosis should preserve successful layers and make the smallest relevant change;
- uninspected media and unverified platform behavior must never be presented as observed facts.

Not carried over: any Seedance 2.0 duration, asset ceiling, model identifier, API field, resolution, price, extension behavior, real-person rule, or provider-specific capability.

## Upstream B: 2.5 adaptation layer

- Repository: https://github.com/ye4wzp/seedance2.5-prompt-skill
- Reviewed commit: `b093438a133ebc3fe81cd1be214271a222516919`
- Reviewed: 2026-09-07
- License: MIT, copyright 2026 Seedance Prompt Skill Contributors

Adapted decision-changing ideas:

- route 2.5 separately from 2.0;
- do not split 19-, 22-, or 30-second 2.5 prompts solely at the old 15-second boundary;
- use timestamp ranges and explicit cross-range locks for longer single prompts;
- make material responsibilities explicit as the reference set grows;
- preserve evidence labels for 2.5 extension, long-video, editing, green-screen/white-model, and real-person-material claims.

The upstream 2.5 notes explicitly say they were built from an official release summary plus third-party reports and had no local case verification at the recorded revision. Some later 2.0-oriented tables in that repository still recommend splitting 16–30 seconds, contradicting its own 2.5 adapter. This skill resolves the conflict in favor of the dedicated 2.5 routing rule while retaining the evidence boundary.

## Local additions

- conditional dialogue-staging gate rather than universal shot/reverse-shot rewriting;
- per-line speaker/face/foreground/position/eyeline/lip/OS/VO/axis ledger;
- Raven/Draven behavioral acceptance cases;
- exact minimal-difference validator and regression cases;
- readable result classes: `确定冲突`, `需要人工判断`, `未触发此检查器`, and `通过`.

## Validation boundary

Repository validation and deterministic tests establish structure and explicit prompt invariants only. They do not validate Seedance 2.5 availability on a particular account, API schema, provider behavior, rendering quality, identity fidelity, lip-sync accuracy, or actual shot continuity. Those require current surface documentation and/or generated-video inspection.
