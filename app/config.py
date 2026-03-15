from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DATA_DIR = Path("data")
QUESTION_FLOW_PATH = DATA_DIR / "question_flow.json"

DEFAULT_QUESTION_FLOW: dict[str, Any] = {
    "version": "v1",
    "sections": [
        {
            "key": "main_concern",
            "title": "主诉问题",
            "required": True,
            "questions": ["你最近最困扰的健康问题是什么？"],
        },
        {
            "key": "lifestyle",
            "title": "生活方式",
            "required": True,
            "questions": ["睡眠、饮食、运动、压力情况如何？"],
        },
        {
            "key": "special_events",
            "title": "特殊事件",
            "required": True,
            "questions": ["近期是否手术、住院或重大治疗？"],
        },
        {
            "key": "medication",
            "title": "用药与禁忌",
            "required": True,
            "questions": ["近期用药、过敏史或医生禁忌有哪些？"],
        },
        {
            "key": "goals",
            "title": "目标与期望",
            "required": True,
            "questions": ["你希望优先改善什么，期望周期多久？"],
        },
    ],
}


def ensure_question_flow() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not QUESTION_FLOW_PATH.exists():
        QUESTION_FLOW_PATH.write_text(json.dumps(DEFAULT_QUESTION_FLOW, ensure_ascii=False, indent=2), encoding="utf-8")


def load_question_flow() -> dict[str, Any]:
    ensure_question_flow()
    return json.loads(QUESTION_FLOW_PATH.read_text(encoding="utf-8"))


def save_question_flow(payload: dict[str, Any]) -> dict[str, Any]:
    ensure_question_flow()
    QUESTION_FLOW_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload

