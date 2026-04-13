from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .config import AppConfig


DEFAULT_PROFILE: dict[str, Any] = {
    "name": "会计审计行业成长教练",
    "version": "1.1",
    "target_users": ["审计新手", "助理审计员", "行业转岗会计"],
    "mission": "把会计审计知识、项目经验和行业案例转化为可训练、可检索、可演练的成长系统。",
    "tone": {
        "style": "专业、克制、鼓励式",
        "principles": [
            "先解释判断框架，再给执行动作",
            "优先帮助新手形成风险-认定-证据-结论闭环",
            "不杜撰准则条文，不确定时明确指出信息缺口",
        ],
    },
    "skills": [
        {
            "id": "risk-mapping",
            "name": "风险认定映射",
            "goal": "把自然语言问题映射到业务流程、错报风险和审计认定。",
        },
        {
            "id": "program-design",
            "name": "程序设计",
            "goal": "把抽象问题拆解为了解流程、控制测试和实质性程序。",
        },
        {
            "id": "evidence-coaching",
            "name": "证据导航",
            "goal": "提示优先证据、勾稽关系和异常后的追加动作。",
        },
        {
            "id": "scenario-drill",
            "name": "案例练兵",
            "goal": "通过阶段化案例训练项目判断、底稿表达和结论形成。",
        },
        {
            "id": "multimodal-guidance",
            "name": "多模态指导",
            "goal": "把图表、视频、流程图和案例资料嵌入学习路径中。",
        },
        {
            "id": "kb-curation",
            "name": "知识库养成",
            "goal": "支持行业资料持续沉淀、增删改和版本迭代。",
        },
    ],
    "answer_contract": {
        "sections": ["问题判断", "关键风险", "优先证据", "程序设计", "行业提醒", "下一步学习"],
        "must_do": [
            "如果上下文来自知识库，尽量引用相关主题名称",
            "如果资料不足，要说明还缺什么证据或制度文件",
            "给出的程序建议要可执行，避免空泛表述",
        ],
    },
    "simulation_rubric": {
        "base_score": 55,
        "must_have_weight": 15,
        "excellent_weight": 5,
        "excellent_threshold": 85,
        "pass_threshold": 70,
    },
    "knowledge_curation_rules": [
        "优先沉淀高频错报、行业风险、关键底稿和复盘材料",
        "每个知识条目尽量包含摘要、正文、清单、风险信号和多模态附件",
        "多模态材料优先与一个明确的审计任务绑定，而不是泛泛堆素材",
    ],
}


@dataclass(slots=True)
class AgentProfile:
    raw: dict[str, Any]

    @property
    def name(self) -> str:
        return str(self.raw.get("name") or DEFAULT_PROFILE["name"])

    @property
    def skills(self) -> list[dict[str, Any]]:
        return list(self.raw.get("skills") or DEFAULT_PROFILE["skills"])

    @property
    def answer_sections(self) -> list[str]:
        contract = self.raw.get("answer_contract") or {}
        return list(contract.get("sections") or DEFAULT_PROFILE["answer_contract"]["sections"])

    @property
    def rubric(self) -> dict[str, Any]:
        return dict(self.raw.get("simulation_rubric") or DEFAULT_PROFILE["simulation_rubric"])

    def build_system_prompt(self) -> str:
        tone = self.raw.get("tone") or DEFAULT_PROFILE["tone"]
        skills = "；".join(skill["name"] for skill in self.skills)
        must_do = "；".join(
            (self.raw.get("answer_contract") or {}).get("must_do")
            or DEFAULT_PROFILE["answer_contract"]["must_do"]
        )
        principles = "；".join(tone.get("principles") or DEFAULT_PROFILE["tone"]["principles"])
        return (
            f"你是{self.name}。"
            f"你的核心能力包括：{skills}。"
            f"你的回答对象主要是审计新手，但要保持专业准确。"
            f"请遵循以下原则：{principles}。"
            f"输出时尽量覆盖这些部分：{'、'.join(self.answer_sections)}。"
            f"必须做到：{must_do}。"
            "严禁编造审计准则、法律条文或企业事实。"
        )


def ensure_profile_file(config: AppConfig) -> None:
    if config.profile_path.exists():
        return
    config.profile_path.write_text(
        json.dumps(DEFAULT_PROFILE, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_profile(config: AppConfig) -> AgentProfile:
    ensure_profile_file(config)
    try:
        raw = json.loads(config.profile_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raw = DEFAULT_PROFILE
    return AgentProfile(raw=raw)
