#!/usr/bin/env python3
"""Deterministic checks for structured Seedance prompt-review ledgers.

This helper deliberately does not infer cinematic meaning from raw prose. A model or
human first extracts semantic facts into the JSON ledger; these checks then enforce
explicit speaker, staging, continuity, and minimal-difference invariants.
"""

from __future__ import annotations

import argparse
import difflib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


DEFINITE = "确定冲突"
JUDGMENT = "需要人工判断"
NOT_TRIGGERED = "未触发此检查器"
PASS = "通过"

FRONT_VIEWS = {"front", "three_quarter", "正脸", "四分之三正脸"}
BACK_VIEWS = {"back", "back_of_head", "shoulder", "背影", "后脑", "肩部"}
OFFSCREEN_MODES = {"OS", "VO", "telephone", "broadcast", "narration", "电话音", "广播", "旁白"}
REVERSE_TRANSITIONS = {"cut", "cut_to_reverse", "cut_to_new_angle", "切镜", "切至反打镜头"}
NO_DIALOGUE_KINDS = {"action", "product", "scenery", "vfx", "动作", "产品", "风景", "纯特效"}


@dataclass(frozen=True)
class Issue:
    category: str
    code: str
    message: str
    time_range: str = "全局"


def _issue(category: str, code: str, message: str, segment: dict[str, Any] | None = None) -> Issue:
    return Issue(category, code, message, str((segment or {}).get("time_range", "全局")))


def dialogue_route(context: dict[str, Any]) -> tuple[bool, list[str]]:
    """Return whether to load the full dialogue-staging module and why."""
    reasons: list[str] = []
    kind = str(context.get("prompt_kind", "")).lower()
    has_dialogue = bool(context.get("has_explicit_dialogue"))
    visible_count = int(context.get("visible_character_count", 0) or 0)

    if kind in NO_DIALOGUE_KINDS and not has_dialogue:
        return False, reasons
    if context.get("single_person_monologue") and visible_count <= 1:
        return False, reasons
    if context.get("only_offscreen_or_voiceover_dialogue"):
        return False, reasons
    if visible_count >= 2 and has_dialogue:
        reasons.append("同场两名或以上可见角色并有明确台词")
    if context.get("speaker_switches_between_segments"):
        reasons.append("相邻时间段说话者切换")
    if context.get("uses_shot_relation_staging"):
        reasons.append("出现越肩/反打/前景背影/对视等镜头关系")
    if context.get("user_reported_staging_error"):
        reasons.append("用户报告说话者、口型、正背面或站位错误")
    return bool(reasons), reasons


def legacy_15s_split_is_invalid(model_line: str, duration_seconds: float) -> bool:
    """Flag only the obsolete reasoning 'over 15 seconds must split' for 2.5.

    This does not assert that a particular account or surface exposes a duration.
    It only prevents a 2.0 ceiling from being used as the reason for splitting.
    """
    normalized = model_line.strip().lower().replace("seedance", "").replace(" ", "")
    return normalized in {"2.5", "25"} and 15 < duration_seconds <= 30


def _visible_non_speakers(segment: dict[str, Any], speaker: str) -> set[str]:
    return {str(name) for name in segment.get("visible_characters", []) if str(name) != speaker}


def _basic_offscreen_checks(segments: Iterable[dict[str, Any]]) -> list[Issue]:
    issues: list[Issue] = []
    for segment in segments:
        speaker = str(segment.get("speaker", ""))
        if not speaker:
            continue
        visible = {str(name) for name in segment.get("visible_characters", [])}
        mode = str(segment.get("dialogue_mode", ""))
        if speaker not in visible and mode not in OFFSCREEN_MODES:
            issues.append(_issue(DEFINITE, "OFFSCREEN_WITHOUT_LABEL", f"{speaker} 不在画面内，但台词未标记 OS/VO/电话音/广播/旁白。", segment))
    return issues


def audit_dialogue_ledger(payload: dict[str, Any]) -> dict[str, Any]:
    context = payload.get("context", {})
    segments = payload.get("segments", [])
    triggered, reasons = dialogue_route(context)
    issues = _basic_offscreen_checks(segments)

    if not triggered:
        status = DEFINITE if issues else NOT_TRIGGERED
        return {"status": status, "triggered": False, "trigger_reasons": reasons, "issues": [asdict(i) for i in issues]}

    fixed_wide = bool(context.get("fixed_wide_two_shot"))
    position_locks = {str(k): str(v) for k, v in context.get("position_locks", {}).items()}
    facing_locks = {str(k): str(v) for k, v in context.get("facing_locks", {}).items()}
    wardrobe_locks = {str(k): str(v) for k, v in context.get("wardrobe_locks", {}).items()}
    anchor_positions: dict[str, str] = {}
    anchor_facing: dict[str, str] = {}
    prior_onscreen_speaker = ""

    for segment in segments:
        visible = [str(name) for name in segment.get("visible_characters", [])]
        speaker = str(segment.get("speaker", ""))
        mode = str(segment.get("dialogue_mode", "onscreen"))
        onscreen = bool(speaker) and mode not in OFFSCREEN_MODES
        relation = str(segment.get("camera_relation", ""))
        positions = {str(k): str(v) for k, v in segment.get("positions", {}).items()}
        facing = {str(k): str(v) for k, v in segment.get("facing", {}).items()}
        wardrobe = {str(k): str(v) for k, v in segment.get("wardrobe", {}).items()}

        for name, side in positions.items():
            if name in position_locks and position_locks[name] != side:
                issues.append(_issue(DEFINITE, "LOCKED_SCREEN_SIDE", f"{name} 应保持 {position_locks[name]} 侧，当前为 {side} 侧。", segment))
            if name in anchor_positions and anchor_positions[name] != side:
                issues.append(_issue(DEFINITE, "SCREEN_SIDE_FLIP", f"{name} 从 {anchor_positions[name]} 侧变为 {side} 侧，未声明轴线重置。", segment))
            anchor_positions.setdefault(name, side)
        for name, direction in facing.items():
            if name in facing_locks and facing_locks[name] != direction:
                issues.append(_issue(DEFINITE, "LOCKED_FACING", f"{name} 应保持面向 {facing_locks[name]}，当前为 {direction}。", segment))
            if name in anchor_facing and anchor_facing[name] != direction:
                issues.append(_issue(DEFINITE, "FACING_FLIP", f"{name} 朝向从 {anchor_facing[name]} 变为 {direction}，未声明轴线重置。", segment))
            anchor_facing.setdefault(name, direction)
        for name, expected_wardrobe in wardrobe_locks.items():
            if name in visible and wardrobe.get(name) != expected_wardrobe:
                issues.append(_issue(DEFINITE, "WARDROBE_LOCK", f"{name} 的服装应保持 {expected_wardrobe}，当前为 {wardrobe.get(name, '未说明')}。", segment))

        if onscreen:
            if speaker not in visible:
                continue
            primary_face = str(segment.get("primary_face", ""))
            if not fixed_wide and primary_face and primary_face != speaker:
                issues.append(_issue(DEFINITE, "WRONG_PRIMARY_FACE", f"台词属于 {speaker}，但主要展示 {primary_face} 的正脸。", segment))
            if not fixed_wide and not primary_face:
                issues.append(_issue(JUDGMENT, "PRIMARY_FACE_UNSPECIFIED", f"{speaker} 说话时未说明主要可读正脸。", segment))

            face_view = str(segment.get("face_views", {}).get(speaker, ""))
            if not fixed_wide and face_view not in FRONT_VIEWS:
                issues.append(_issue(DEFINITE, "SPEAKER_FACE_NOT_READABLE", f"{speaker} 说话时未锁定正脸或四分之三正脸。", segment))
            if not fixed_wide and segment.get("mouth_unobstructed") is not True:
                issues.append(_issue(JUDGMENT, "MOUTH_VISIBILITY_UNCLEAR", f"{speaker} 的嘴部无遮挡状态未明确。", segment))

            if relation in {"over_shoulder", "reverse_over_shoulder", "越肩", "反打越肩"}:
                foreground = str(segment.get("foreground_character", ""))
                foreground_view = str(segment.get("foreground_view", ""))
                expected_listeners = _visible_non_speakers(segment, speaker)
                if not foreground or foreground not in expected_listeners:
                    issues.append(_issue(DEFINITE, "OTS_FOREGROUND_MISSING", "越肩/反打镜头未明确由非说话者占据前景。", segment))
                if foreground_view not in BACK_VIEWS:
                    issues.append(_issue(DEFINITE, "OTS_FOREGROUND_NOT_BACK", "越肩/反打镜头未明确前景人物为背影、后脑或肩部。", segment))

            lip_sync = {str(name) for name in segment.get("lip_sync_allowed", [])}
            if lip_sync != {speaker}:
                issues.append(_issue(DEFINITE, "LIP_SYNC_OWNER", f"口型归属应且只能是 {speaker}，当前为 {sorted(lip_sync)}。", segment))
            silent = {str(name) for name in segment.get("silent_characters", [])}
            missing_silent = _visible_non_speakers(segment, speaker) - silent
            if missing_silent:
                issues.append(_issue(DEFINITE, "LISTENER_SILENCE_MISSING", f"可见非说话者未明确保持沉默：{', '.join(sorted(missing_silent))}。", segment))

            readable_fronts = {str(name) for name in segment.get("readable_front_faces", [])}
            if len(readable_fronts) > 1 and lip_sync != {speaker}:
                issues.append(_issue(DEFINITE, "TWO_FACES_AMBIGUOUS", "两人均露出可读正脸，但没有唯一口型归属。", segment))

            if segment.get("axis_180_maintained") is False:
                issues.append(_issue(DEFINITE, "AXIS_BROKEN", "反打后未保持 180 度轴线。", segment))
            if relation in {"over_shoulder", "reverse_over_shoulder", "越肩", "反打越肩"} and "axis_180_maintained" not in segment:
                issues.append(_issue(JUDGMENT, "AXIS_UNSPECIFIED", "越肩/反打关系未说明是否保持 180 度轴线。", segment))

            if prior_onscreen_speaker and prior_onscreen_speaker != speaker and not fixed_wide:
                transition = str(segment.get("camera_transition", ""))
                if transition not in REVERSE_TRANSITIONS:
                    issues.append(_issue(DEFINITE, "SPEAKER_SWITCH_WITHOUT_CUT", f"说话者从 {prior_onscreen_speaker} 切换为 {speaker}，但未明确切镜或反打。", segment))
            prior_onscreen_speaker = speaker

        turns = [str(name) for name in segment.get("speaker_turns", [])]
        if len(set(turns)) > 1 and not fixed_wide:
            transition = str(segment.get("camera_transition", ""))
            if transition not in REVERSE_TRANSITIONS:
                issues.append(_issue(DEFINITE, "MULTI_TURN_FOCUS_ONLY", "同一时间段换人说话，但只写焦点变化或未写切至反打机位。", segment))

    definite = any(i.category == DEFINITE for i in issues)
    judgment = any(i.category == JUDGMENT for i in issues)
    status = DEFINITE if definite else JUDGMENT if judgment else PASS
    return {"status": status, "triggered": True, "trigger_reasons": reasons, "issues": [asdict(i) for i in issues]}


def verify_minimal_difference(payload: dict[str, Any]) -> dict[str, Any]:
    original = str(payload.get("original", ""))
    revised = str(payload.get("revised", ""))
    expected = original
    issues: list[Issue] = []

    for index, item in enumerate(payload.get("allowed_replacements", []), start=1):
        old = str(item.get("old", ""))
        new = str(item.get("new", ""))
        count = int(item.get("count", 1))
        actual = expected.count(old)
        if not old or actual != count:
            issues.append(_issue(DEFINITE, "REPLACEMENT_SCOPE_INVALID", f"允许修改项 {index} 的原片段应出现 {count} 次，实际为 {actual} 次。"))
            continue
        expected = expected.replace(old, new, count)

    if expected != revised:
        diff = "\n".join(difflib.unified_diff(expected.splitlines(), revised.splitlines(), fromfile="expected", tofile="revised", lineterm=""))
        issues.append(_issue(DEFINITE, "OUTSIDE_SCOPE_CHANGED", "最终稿包含允许替换之外的变化。\n" + diff))

    return {"status": DEFINITE if issues else PASS, "issues": [asdict(i) for i in issues]}


def _print_result(result: dict[str, Any]) -> None:
    print(f"结果：{result['status']}")
    if "triggered" in result:
        print(f"对白站位完整检查：{'已触发' if result['triggered'] else '未触发'}")
        for reason in result.get("trigger_reasons", []):
            print(f"  - 触发原因：{reason}")
    if not result.get("issues"):
        print("问题：无")
        return
    print("问题：")
    for item in result["issues"]:
        print(f"  - [{item['category']}] {item['time_range']} {item['code']}: {item['message']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("dialogue", "minimal-diff"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--input", required=True, type=Path, help="UTF-8 JSON input")
        sub.add_argument("--json", action="store_true", help="print JSON instead of readable text")
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = audit_dialogue_ledger(payload) if args.command == "dialogue" else verify_minimal_difference(payload)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_result(result)
    return 1 if result["status"] == DEFINITE else 0


if __name__ == "__main__":
    raise SystemExit(main())
