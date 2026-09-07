# Continuity review

Load this module for multi-range, multi-shot, multi-character, changing-state, or continuation prompts.

## Continuity ledger

Track only dimensions present in the prompt:

| Dimension | Record across ranges |
|---|---|
| Character | exact tag/name, identity, wardrobe, hair, carried prop, visible state |
| Space | location, left/right, foreground/background, facing, eyeline, screen direction |
| Action | initial state, trigger, decisive change, follow-through, endpoint |
| Prop | owner, hand, position, orientation, intact/damaged/open/closed state |
| Light | physical source, direction, color/phase, declared transition |
| Camera | shot size, angle, axis side, primary move, start and end composition |
| Sound | speaker, OS/VO state, ambience, music phase, synchronized cue |
| Reference | exact tag and the dimension it controls |

## Conflict rules

Treat these as definite conflicts unless a transition is explicitly authored:

- one character or tag silently becomes another;
- wardrobe, prop ownership, location, or persistent environment changes without permission;
- a later range starts before the prior range's decisive action or endpoint has occurred;
- mutually exclusive actions occur at the same time;
- a completed action repeats as if it had not happened;
- left/right, eyeline, screen direction, or light direction flips without a cut or intentional axis reset;
- a reference is renamed, renumbered, or assigned two incompatible owners;
- the declared total duration contains an uncovered gap or unintended overlap.

Mark missing information as `需要人工判断` when the prompt remains viable under more than one interpretation. Do not manufacture a lock the user never stated.

## Multi-range procedure

1. Build a row per time range.
2. Compare each range's opening state with the previous range's endpoint.
3. Check that every requested beat appears once and only once.
4. Check persistent anchors at every change of framing, not only in the opening paragraph.
5. Check sound and dialogue independently of the visible subject.
6. For an accepted previous video, actual observed end state outranks the planned end state. If the media was not inspected, label the state user-reported or unknown.
7. Repair the smallest failing dimension. A lighting error does not authorize a new performance; a prop error does not authorize new dialogue.

## Camera and action density

- One short shot normally has one primary move.
- A compatible dual-axis move is acceptable when it describes one coherent path and does not hide the key action.
- Keep subject motion, prop motion, camera motion, and environmental motion under separate owners.
- Use the segment endpoint intentionally: resolved end, handoff/open motion, loop seam, hero hold, edit point, or reveal. Do not leave unconsumed drift by accident.
