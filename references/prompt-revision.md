# Existing-prompt revision

Use this module for every requested prompt optimization. It is a repair workflow, not an invitation to replace the user's idea.

## Intake ledger

Record internally:

- requested change;
- explicitly editable span;
- locked plot, dialogue, character labels, wardrobe, props, scene, timestamps, total duration, aspect ratio, sound, and reference tags;
- target Seedance line and surface, when known;
- review-only versus revision;
- output requested as full replacement, comparison, or issue list.

If the editable span is ambiguous but a narrow interpretation is safe, use it and say what was treated as locked. Ask only when two plausible scopes would produce materially different edits.

## Basic optimization pass

- Delete or replace empty, repeated, or conflicting quality language. `电影感`, `史诗级`, `唯美`, `8K`, `masterpiece`, and render-engine name stacks do not substitute for a physical decision.
- Express the visible brief through subject, action, scene, framing, camera movement, motivated light source, sound, and end state. Do not add every field when the original does not need it.
- For a fragile action, use: `initial state → trigger → decisive change → follow-through → segment-end state`. Name what the camera actually covers.
- Prefer one primary move per short shot. Use two axes only when they are physically compatible and the combined move serves the same action; do not stack unrelated push, orbit, crane, pan, and rack-focus commands.
- Replace feelings with observable performance only when the user allowed performance edits. Do not invent motives, dialogue, or story turns.
- Keep important face, hand, prop, label, and text requirements compatible with framing and motion. If the shot is overloaded, identify the tradeoff; do not silently drop the user's must-have.

## Reference contracts

Assign each referenced asset a primary responsibility such as identity, wardrobe, product, first frame, end frame, environment, motion, camera, timing, audio, or style. State what must not transfer when roles could bleed together.

- Canonical identity controls enduring appearance.
- An accepted previous clip/final frame controls the transient opening state.
- A donor motion or camera reference must not overwrite identity, wardrobe, product geometry, environment, or accepted state unless the user explicitly says so.
- Preserve literal tags exactly, including spacing, case, language, and numbering.
- Do not infer a universal Seedance 2.5 tag syntax from Seedance 2.0. Use the user's existing tags or currently verified surface syntax.

## Minimal-difference mode

When the user says “只修改画面”, “其他内容保持不变”, “只改这一段”, or equivalent:

1. Quote or internally delimit the exact replaceable span.
2. Treat every byte outside that span as locked, including whitespace when the user requests literal preservation.
3. Make only the requested semantic change inside the span; do not opportunistically polish neighboring text.
4. Search the full revised prompt for residue from the old state, contradictory action, missing coverage, and changed tags.
5. Compare original and final after applying only the declared replacement. `scripts/prompt_review_checks.py minimal-diff` can enforce this exact invariant.
6. Return the complete final prompt by default. A diff may accompany it, but never replace it unless the user requests only a patch.

## Review labels

- `确定冲突`: the prompt states mutually incompatible facts or violates an explicit lock.
- `需要人工判断`: the prompt omits enough staging or platform context that more than one valid interpretation remains.
- `未触发此检查器`: a conditional module is outside the prompt's risk profile.
- `建议优化`: optional craft improvement that is not an error and must not override locked content.

Never describe a stylistic preference as a definite technical failure.
