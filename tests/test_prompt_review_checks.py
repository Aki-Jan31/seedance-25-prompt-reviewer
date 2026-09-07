import importlib.util
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "prompt_review_checks.py"
SPEC = importlib.util.spec_from_file_location("prompt_review_checks", SCRIPT)
CHECKS = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = CHECKS
SPEC.loader.exec_module(CHECKS)


def dialogue_payload(**overrides):
    context = {
        "prompt_kind": "dialogue",
        "has_explicit_dialogue": True,
        "visible_character_count": 2,
        "speaker_switches_between_segments": False,
        "uses_shot_relation_staging": True,
        "position_locks": {"Draven": "left", "Raven": "right"},
        "facing_locks": {"Draven": "right", "Raven": "left"},
        "wardrobe_locks": {"Draven": "black_armor", "Raven": "red_robe"},
    }
    context.update(overrides)
    return {"context": context, "segments": []}


def correct_segment(speaker, listener, speaker_side, listener_side, speaker_facing, listener_facing):
    return {
        "time_range": "0-5秒",
        "visible_characters": ["Draven", "Raven"],
        "speaker": speaker,
        "dialogue_mode": "onscreen",
        "primary_face": speaker,
        "face_views": {speaker: "three_quarter", listener: "back"},
        "mouth_unobstructed": True,
        "foreground_character": listener,
        "foreground_view": "back",
        "camera_relation": "reverse_over_shoulder",
        "positions": {speaker: speaker_side, listener: listener_side},
        "facing": {speaker: speaker_facing, listener: listener_facing},
        "wardrobe": {"Draven": "black_armor", "Raven": "red_robe"},
        "readable_front_faces": [speaker],
        "lip_sync_allowed": [speaker],
        "silent_characters": [listener],
        "axis_180_maintained": True,
    }


class RavenDravenBehaviorTests(unittest.TestCase):
    def test_wrong_draven_line_still_shows_raven_face(self):
        payload = dialogue_payload()
        payload["segments"] = [{
            "time_range": "6-10秒",
            "visible_characters": ["Draven", "Raven"],
            "speaker": "Draven",
            "dialogue_mode": "onscreen",
            "primary_face": "Raven",
            "face_views": {"Raven": "front", "Draven": "hidden"},
            "mouth_unobstructed": False,
            "camera_relation": "reverse_over_shoulder",
            "positions": {"Draven": "left", "Raven": "right"},
            "facing": {"Draven": "right", "Raven": "left"},
            "wardrobe": {"Draven": "black_armor", "Raven": "red_robe"},
            "readable_front_faces": ["Raven"],
            "lip_sync_allowed": ["Raven"],
            "silent_characters": [],
            "axis_180_maintained": True,
        }]
        result = CHECKS.audit_dialogue_ledger(payload)
        codes = {issue["code"] for issue in result["issues"]}
        self.assertEqual(result["status"], CHECKS.DEFINITE)
        self.assertIn("WRONG_PRIMARY_FACE", codes)
        self.assertIn("OTS_FOREGROUND_MISSING", codes)
        self.assertIn("OTS_FOREGROUND_NOT_BACK", codes)

    def test_correct_draven_reverse_passes(self):
        payload = dialogue_payload()
        payload["segments"] = [correct_segment("Draven", "Raven", "left", "right", "right", "left")]
        self.assertEqual(CHECKS.audit_dialogue_ledger(payload)["status"], CHECKS.PASS)

    def test_correct_raven_direction_passes(self):
        payload = dialogue_payload()
        payload["segments"] = [correct_segment("Raven", "Draven", "right", "left", "left", "right")]
        self.assertEqual(CHECKS.audit_dialogue_ledger(payload)["status"], CHECKS.PASS)

    def test_single_person_monologue_does_not_force_reverse_shot(self):
        payload = dialogue_payload(
            visible_character_count=1,
            uses_shot_relation_staging=False,
            single_person_monologue=True,
        )
        payload["segments"] = [{
            "time_range": "0-8秒",
            "visible_characters": ["Raven"],
            "speaker": "Raven",
            "dialogue_mode": "onscreen",
        }]
        result = CHECKS.audit_dialogue_ledger(payload)
        self.assertFalse(result["triggered"])
        self.assertEqual(result["status"], CHECKS.NOT_TRIGGERED)

    def test_draven_os_does_not_require_face_but_label_is_checked(self):
        payload = dialogue_payload(
            visible_character_count=1,
            uses_shot_relation_staging=False,
            only_offscreen_or_voiceover_dialogue=True,
        )
        payload["segments"] = [{
            "time_range": "0-5秒",
            "visible_characters": ["Raven"],
            "speaker": "Draven",
            "dialogue_mode": "OS",
        }]
        result = CHECKS.audit_dialogue_ledger(payload)
        self.assertFalse(result["triggered"])
        self.assertEqual(result["status"], CHECKS.NOT_TRIGGERED)
        self.assertEqual(result["issues"], [])

    def test_missing_os_label_is_definite_conflict(self):
        payload = dialogue_payload(
            visible_character_count=1,
            uses_shot_relation_staging=False,
            only_offscreen_or_voiceover_dialogue=True,
        )
        payload["segments"] = [{
            "time_range": "0-5秒",
            "visible_characters": ["Raven"],
            "speaker": "Draven",
            "dialogue_mode": "onscreen",
        }]
        result = CHECKS.audit_dialogue_ledger(payload)
        self.assertEqual(result["status"], CHECKS.DEFINITE)
        self.assertEqual(result["issues"][0]["code"], "OFFSCREEN_WITHOUT_LABEL")

    def test_two_speakers_with_focus_shift_only_is_flagged(self):
        payload = dialogue_payload(speaker_switches_between_segments=True)
        segment = correct_segment("Raven", "Draven", "right", "left", "left", "right")
        segment.update({
            "time_range": "0-8秒",
            "speaker_turns": ["Raven", "Draven"],
            "camera_transition": "focus_shift",
        })
        payload["segments"] = [segment]
        result = CHECKS.audit_dialogue_ledger(payload)
        self.assertIn("MULTI_TURN_FOCUS_ONLY", {issue["code"] for issue in result["issues"]})

    def test_user_locked_fixed_wide_does_not_force_reverse_shot(self):
        payload = dialogue_payload(
            uses_shot_relation_staging=False,
            fixed_wide_two_shot=True,
        )
        payload["segments"] = [{
            "time_range": "0-5秒",
            "visible_characters": ["Draven", "Raven"],
            "speaker": "Raven",
            "dialogue_mode": "onscreen",
            "camera_relation": "fixed_two_shot",
            "positions": {"Draven": "left", "Raven": "right"},
            "facing": {"Draven": "right", "Raven": "left"},
            "wardrobe": {"Draven": "black_armor", "Raven": "red_robe"},
            "lip_sync_allowed": ["Raven"],
            "silent_characters": ["Draven"],
            "axis_180_maintained": True,
        }]
        result = CHECKS.audit_dialogue_ledger(payload)
        self.assertTrue(result["triggered"])
        self.assertEqual(result["status"], CHECKS.PASS)

    def test_missing_mouth_visibility_is_human_judgment_not_definite_conflict(self):
        payload = dialogue_payload(uses_shot_relation_staging=False)
        segment = correct_segment("Raven", "Draven", "right", "left", "left", "right")
        segment["camera_relation"] = "medium_two_shot"
        segment.pop("mouth_unobstructed")
        payload["segments"] = [segment]
        result = CHECKS.audit_dialogue_ledger(payload)
        self.assertEqual(result["status"], CHECKS.JUDGMENT)
        self.assertEqual(result["issues"][0]["code"], "MOUTH_VISIBILITY_UNCLEAR")

    def test_readable_output_lists_category_time_and_code(self):
        result = {
            "status": CHECKS.DEFINITE,
            "triggered": True,
            "trigger_reasons": ["示例触发原因"],
            "issues": [{
                "category": CHECKS.DEFINITE,
                "time_range": "6-10秒",
                "code": "WRONG_PRIMARY_FACE",
                "message": "台词与主要正脸不一致。",
            }],
        }
        output = io.StringIO()
        with redirect_stdout(output):
            CHECKS._print_result(result)
        rendered = output.getvalue()
        self.assertIn("结果：确定冲突", rendered)
        self.assertIn("6-10秒 WRONG_PRIMARY_FACE", rendered)


class RoutingAndMinimalDiffTests(unittest.TestCase):
    def test_2_5_durations_are_not_split_by_the_legacy_15_second_rule(self):
        for duration in (19, 22, 30):
            with self.subTest(duration=duration):
                self.assertTrue(CHECKS.legacy_15s_split_is_invalid("Seedance 2.5", duration))
        self.assertFalse(CHECKS.legacy_15s_split_is_invalid("Seedance 2.0", 22))

    def test_pure_action_does_not_trigger_dialogue_checker(self):
        payload = {
            "context": {
                "prompt_kind": "action",
                "has_explicit_dialogue": False,
                "visible_character_count": 3,
                "uses_shot_relation_staging": False,
            },
            "segments": [],
        }
        result = CHECKS.audit_dialogue_ledger(payload)
        self.assertFalse(result["triggered"])
        self.assertEqual(result["status"], CHECKS.NOT_TRIGGERED)

    def test_only_visual_span_changes_and_everything_else_is_byte_identical(self):
        original = (
            "模型：Seedance 2.5\n时长：22秒\n角色：@Raven红袍、@Draven黑甲\n"
            "0-8秒：Raven站在右侧说：\"你终于来了。\"\n"
            "8-15秒：旧画面：镜头绕场三周。\n"
            "15-22秒：Draven（OS）说：\"门已经关上。\"\n声音：雨声持续"
        )
        revised = original.replace("旧画面：镜头绕场三周。", "新画面：固定中景，窗外闪电照亮两人轮廓。")
        result = CHECKS.verify_minimal_difference({
            "original": original,
            "revised": revised,
            "allowed_replacements": [{
                "old": "旧画面：镜头绕场三周。",
                "new": "新画面：固定中景，窗外闪电照亮两人轮廓。",
                "count": 1,
            }],
        })
        self.assertEqual(result["status"], CHECKS.PASS)
        self.assertIn("@Raven红袍、@Draven黑甲", revised)
        self.assertIn("Draven（OS）说：\"门已经关上。\"", revised)
        self.assertIn("时长：22秒", revised)

    def test_minimal_diff_detects_changed_dialogue_outside_scope(self):
        original = "画面：旧画面。\n台词：Raven：\"别动。\"\n时长：19秒"
        revised = "画面：新画面。\n台词：Raven：\"快走。\"\n时长：19秒"
        result = CHECKS.verify_minimal_difference({
            "original": original,
            "revised": revised,
            "allowed_replacements": [{"old": "旧画面。", "new": "新画面。"}],
        })
        self.assertEqual(result["status"], CHECKS.DEFINITE)
        self.assertEqual(result["issues"][0]["code"], "OUTSIDE_SCOPE_CHANGED")


if __name__ == "__main__":
    unittest.main()
