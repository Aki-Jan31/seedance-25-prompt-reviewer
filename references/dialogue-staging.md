# Conditional dialogue staging

Load this full module only under the trigger gate in `SKILL.md`. It audits who is visible, who speaks, who owns the mouth movement, and whether shot/reverse-shot geography remains coherent. It does not require every conversation to use over-shoulder coverage.

## Internal per-line table

Before revising, create one row per spoken turn with at least:

| Field | Question |
|---|---|
| Time range | When does the turn occur? |
| Visible characters | Who is inside the frame? |
| Actual speaker | Who owns the exact line? |
| Speaker face | Whose front or three-quarter face should be readable? |
| Foreground character | Who occupies the foreground, if anyone? |
| Foreground view | Front, back, back of head, or shoulder? |
| Left/right | Where does each person remain on screen? |
| Facing and eyeline | Which way does each face and look? |
| Lip-sync owner | Who alone may show speaking mouth movement? |
| Silent listeners | Which visible non-speakers must remain silent? |
| Dialogue mode | On-screen, OS, VO, telephone, broadcast, or narration? |
| Cut requirement | Does the speaker change require a cut/reverse shot? |
| Axis | Is the 180-degree axis preserved or intentionally reset? |

Keep this table internal unless the user asks to see it. It is a reasoning aid, not replacement prompt prose.

## Default staging rules

- An on-screen speaker should have a clear front or three-quarter face, unobstructed mouth, and explicit focus when lip-sync matters.
- In an over-shoulder setup, the listener occupies the foreground only as back, back of head, or shoulder; the listener does not face camera or move their mouth.
- When the speaker changes in shot/reverse-shot coverage, write the cut time or `切至反打镜头`. A rack focus or `焦点转移` alone does not exchange camera sides or foreground roles.
- Preserve the established 180-degree axis, screen-left/right positions, facing, and eyelines through the reverse.
- Name the only lip-sync owner and make visible non-speakers explicitly silent when ambiguity is plausible.
- If a speaker is outside the frame, mark the line `OS`. `VO` and narration do not require a visible speaker face.
- Respect user-locked two-shots, fixed wides, profile two-shots, or other compositions. In those cases, clarify mouth ownership without forcing over-shoulder coverage.

## Definite problems

Report each as `确定冲突`:

- Draven's line is paired with Raven as the primary readable face, or the reverse;
- an over-shoulder/reverse shot does not state that the foreground listener is shown from behind, by the back of the head, or by the shoulder;
- both characters show front/readable faces but no single lip-sync owner or silent listener is named where ambiguity exists;
- a speaker change retains the prior primary face and only says `焦点转移`;
- the reverse flips established left/right positions, facing, eyeline, or axis without an intentional reset;
- an off-screen speaker's line lacks `OS` or an unambiguous equivalent;
- the visible non-speaker is not held silent where the setup could assign the wrong mouth.

## Raven / Draven spatial contract

Use this as a behavioral example, not as a universal naming convention:

- Draven stays screen-left, facing right.
- Raven stays screen-right, facing left.
- Raven speaking: over Draven's back/shoulder; Draven is left foreground back view, Raven is right medium-close front or three-quarter face, only Raven has lip movement.
- Draven speaking: reverse over Raven's back/shoulder; Raven is right foreground back view, Draven is left medium-close front or three-quarter face, only Draven has lip movement.
- A speaker change uses an explicit cut/reverse and keeps the same 180-degree axis.

The deterministic helper accepts a structured version of this table. It can prove stated contradictions in that ledger; it cannot prove that an unstructured prompt was extracted correctly or that the model will render the staging correctly.
