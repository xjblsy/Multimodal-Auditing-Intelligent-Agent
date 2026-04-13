from __future__ import annotations

import json
from collections import OrderedDict
from typing import Any

from .config import AppConfig
from .kb import KnowledgeBase, tokenize_for_search
from .llm import BaseProvider, ModelError
from .profile import AgentProfile


class AuditCoach:
    def __init__(
        self,
        config: AppConfig,
        kb: KnowledgeBase,
        provider: BaseProvider,
        profile: AgentProfile,
    ) -> None:
        self.config = config
        self.kb = kb
        self.provider = provider
        self.profile = profile

    def answer_query(
        self,
        query: str,
        industry: str = "",
        tags: list[str] | None = None,
        scenario_id: str | None = None,
    ) -> dict[str, Any]:
        tags = tags or []
        items = self.kb.search(query=query, industry=industry, tags=tags, limit=5)
        scenario = self.kb.get_scenario(scenario_id) if scenario_id else None
        response = self._build_fallback_answer(query, items, industry, scenario)

        if self.provider.available:
            user_prompt = json.dumps(
                {
                    "query": query,
                    "industry": industry or self.config.default_industry,
                    "scenario": scenario,
                    "knowledge_context": [
                        {
                            "title": item["title"],
                            "summary": item["summary"],
                            "checklist": item["checklist"][:4],
                            "red_flags": item["red_flags"][:4],
                            "related_ids": item.get("related_ids", []),
                        }
                        for item in items
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
            try:
                result = self.provider.generate(self.profile.build_system_prompt(), user_prompt)
                response["answer"] = result.text
                response["answer_source"] = f"{result.provider}:{result.model}"
            except ModelError as exc:
                response["model_notice"] = str(exc)

        return response

    def build_learning_path(
        self,
        industry: str,
        role: str,
        target_level: str,
    ) -> dict[str, Any]:
        items = self.kb.list_items()
        focused = [item for item in items if industry in item["industries"] or "通用" in item["industries"]]
        stage_names = ["打底", "入场", "攻坚", "行业深化"]

        if target_level == "初级":
            selected = focused[:3]
        elif target_level == "高级":
            selected = focused[:7]
        else:
            selected = focused[:5]

        lanes: list[dict[str, Any]] = []
        for stage_name, chunk in zip(stage_names, self._chunk(selected, 2), strict=False):
            lanes.append(
                {
                    "stage": stage_name,
                    "items": [
                        {
                            "id": item["id"],
                            "title": item["title"],
                            "summary": item["summary"],
                            "difficulty": item["difficulty"],
                            "tags": item["tags"],
                        }
                        for item in chunk
                    ],
                }
            )

        return {
            "industry": industry,
            "role": role,
            "target_level": target_level,
            "profile_name": self.profile.name,
            "skills": self.profile.skills,
            "strategy": [
                f"先按 {industry} 场景理解主要错报风险，再回到审计认定和程序设计。",
                f"以 {role} 的工作职责为主线，每学完一个主题都落到样本抽查与底稿表达。",
                "每周至少完成一个模拟案例，形成“风险识别-证据获取-结论表达”闭环。",
            ],
            "lanes": lanes,
        }

    def evaluate_scenario(self, scenario_id: str, stage_id: str, answer: str) -> dict[str, Any]:
        scenario = self.kb.get_scenario(scenario_id)
        if not scenario:
            raise KeyError(f"Scenario not found: {scenario_id}")

        stage = next((item for item in scenario["stages"] if item["id"] == stage_id), None)
        if not stage:
            raise KeyError(f"Stage not found: {stage_id}")

        text = answer.lower()
        answer_tokens = tokenize_for_search(answer)
        must_have_hits = [
            point
            for point in stage["must_have"]
            if point.lower() in text or tokenize_for_search(point).intersection(answer_tokens)
        ]
        excellent_hits = [
            point
            for point in stage["excellent_signals"]
            if point.lower() in text or tokenize_for_search(point).intersection(answer_tokens)
        ]
        missing = [point for point in stage["must_have"] if point not in must_have_hits]

        rubric = self.profile.rubric
        score = int(rubric.get("base_score", 55))
        score += min(len(must_have_hits) * int(rubric.get("must_have_weight", 15)), 30)
        score += min(len(excellent_hits) * int(rubric.get("excellent_weight", 5)), 15)
        score = min(score, 100)

        excellent_threshold = int(rubric.get("excellent_threshold", 85))
        pass_threshold = int(rubric.get("pass_threshold", 70))
        level = "优秀" if score >= excellent_threshold else "合格" if score >= pass_threshold else "待加强"

        return {
            "scenario_id": scenario_id,
            "stage_id": stage_id,
            "score": score,
            "level": level,
            "hits": must_have_hits,
            "excellent_hits": excellent_hits,
            "missing": missing,
            "feedback": [
                f"你已经抓住了 {len(must_have_hits)} 个关键动作。",
                f"还可以补上这些要点: {'；'.join(missing) if missing else '无明显缺口。'}",
                stage["coach_tip"] or "下一步请把审计程序写得更可执行。",
            ],
        }

    def _chunk(self, items: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
        return [items[index : index + size] for index in range(0, len(items), size)]

    def _build_fallback_answer(
        self,
        query: str,
        items: list[dict[str, Any]],
        industry: str,
        scenario: dict[str, Any] | None,
    ) -> dict[str, Any]:
        reasoning_frame: list[str] = []
        if industry:
            reasoning_frame.append(f"先把问题映射到 {industry} 的业务流程和关键认定。")
        reasoning_frame.extend(
            [
                "先识别错报风险，再反推需要什么证据。",
                "把审计动作拆成了解流程、控制测试、实质性程序三层。",
                "回答时同步提醒常见舞弊信号、底稿表达和行业特殊风险。",
            ]
        )

        evidence_focus = self._unique_lines(items, "checklist", limit=6)
        red_flags = self._unique_lines(items, "red_flags", limit=5)
        learning = [item["title"] for item in items[:3]]
        citations = [{"id": item["id"], "title": item["title"]} for item in items]
        related_assets = self._collect_assets(items)

        answer_lines = [
            f"问题判断: {query}",
            "",
            "关键风险:",
        ]
        for step in reasoning_frame[:4]:
            answer_lines.append(f"- {step}")

        if evidence_focus:
            answer_lines.append("")
            answer_lines.append("优先证据:")
            for point in evidence_focus:
                answer_lines.append(f"- {point}")

        answer_lines.append("")
        answer_lines.append("程序设计:")
        answer_lines.append("- 先做流程了解，确认业务链条和控制点。")
        answer_lines.append("- 再做重点样本测试，把异常样本延伸到期后、审批和系统日志。")
        answer_lines.append("- 对重大异常形成可量化的财务影响判断。")

        if red_flags:
            answer_lines.append("")
            answer_lines.append("行业提醒:")
            for point in red_flags:
                answer_lines.append(f"- {point}")

        if scenario:
            answer_lines.append("")
            answer_lines.append(f"下一步学习: 可结合演练案例《{scenario['title']}》")
            answer_lines.append(f"- 背景: {scenario['background']}")
            if scenario["stages"]:
                answer_lines.append(f"- 当前建议先处理: {scenario['stages'][0]['title']}")
        elif learning:
            answer_lines.append("")
            answer_lines.append("下一步学习:")
            for title in learning:
                answer_lines.append(f"- {title}")

        if not items:
            answer_lines.append("")
            answer_lines.append("当前知识库命中较少，建议补充该行业的底稿、制度、案例和流程图材料后再细化。")

        return {
            "answer": "\n".join(answer_lines),
            "answer_source": "local-rag",
            "reasoning_frame": reasoning_frame,
            "recommended_actions": evidence_focus,
            "red_flags": red_flags,
            "learning_suggestions": learning,
            "related_assets": related_assets,
            "citations": citations,
            "profile": {
                "name": self.profile.name,
                "skills": self.profile.skills,
                "answer_sections": self.profile.answer_sections,
            },
        }

    def _unique_lines(
        self,
        items: list[dict[str, Any]],
        key: str,
        limit: int,
    ) -> list[str]:
        ordered: OrderedDict[str, None] = OrderedDict()
        for item in items:
            for value in item.get(key, []):
                text = str(value).strip()
                if text and text not in ordered:
                    ordered[text] = None
                if len(ordered) >= limit:
                    return list(ordered.keys())
        return list(ordered.keys())

    def _collect_assets(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        assets: list[dict[str, Any]] = []
        for item in items:
            modalities = item.get("modalities") or {}
            for group in ("visuals", "videos", "tables"):
                for asset in modalities.get(group, []):
                    assets.append({"knowledge_id": item["id"], "knowledge_title": item["title"], **asset})
        return assets[:8]
