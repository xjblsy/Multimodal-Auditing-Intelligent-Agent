from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import AppConfig


@dataclass(slots=True)
class ComplianceStandard:
    id: str
    name: str
    description: str
    category: str  # 审计准则、会计准则、法律法规等
    version: str
    effective_date: str
    requirements: List[str]


@dataclass(slots=True)
class ComplianceCheckResult:
    standard_id: str
    standard_name: str
    compliant: bool
    issues: List[str]
    recommendations: List[str]
    evidence_required: List[str]


class ComplianceChecker:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.standards_file = config.data_dir / "compliance_standards.json"
        self.load_standards()

    def load_standards(self) -> None:
        if self.standards_file.exists():
            try:
                with open(self.standards_file, "r", encoding="utf-8") as f:
                    standards_data = json.load(f)
                    self.standards = [ComplianceStandard(**standard) for standard in standards_data]
            except (json.JSONDecodeError, ValueError):
                # 文件格式不正确，使用默认合规标准
                self._initialize_default_standards()
        else:
            # 文件不存在，使用默认合规标准
            self._initialize_default_standards()
    
    def _initialize_default_standards(self) -> None:
        # 初始化默认合规标准
        self.standards = [
            ComplianceStandard(
                id="standard_1",
                name="中国注册会计师审计准则第1101号",
                description="财务报表审计的目标和一般原则",
                category="审计准则",
                version="2022年修订",
                effective_date="2023-01-01",
                requirements=[
                    "注册会计师应当按照审计准则的规定执行审计工作",
                    "注册会计师应当获取充分、适当的审计证据",
                    "注册会计师应当保持职业怀疑态度",
                    "注册会计师应当按照审计准则的规定出具审计报告"
                ]
            ),
            ComplianceStandard(
                id="standard_2",
                name="中国注册会计师审计准则第1211号",
                description="通过了解被审计单位及其环境识别和评估重大错报风险",
                category="审计准则",
                version="2022年修订",
                effective_date="2023-01-01",
                requirements=[
                    "注册会计师应当了解被审计单位及其环境",
                    "注册会计师应当识别和评估财务报表层次和认定层次的重大错报风险",
                    "注册会计师应当针对评估的重大错报风险设计和实施审计程序"
                ]
            ),
            ComplianceStandard(
                id="standard_3",
                name="企业会计准则第1号——存货",
                description="规范存货的确认、计量和相关信息的披露",
                category="会计准则",
                version="2006年发布",
                effective_date="2007-01-01",
                requirements=[
                    "存货应当按照成本进行初始计量",
                    "存货成本包括采购成本、加工成本和其他成本",
                    "企业应当采用先进先出法、加权平均法或者个别计价法确定发出存货的实际成本",
                    "资产负债表日，存货应当按照成本与可变现净值孰低计量"
                ]
            ),
            ComplianceStandard(
                id="standard_4",
                name="中华人民共和国会计法",
                description="规范会计行为，保证会计资料真实、完整",
                category="法律法规",
                version="2017年修订",
                effective_date="2017-11-05",
                requirements=[
                    "各单位必须依法设置会计账簿，并保证其真实、完整",
                    "会计机构、会计人员必须按照国家统一的会计制度的规定对原始凭证进行审核",
                    "单位负责人对本单位的会计工作和会计资料的真实性、完整性负责",
                    "任何单位或者个人不得以任何方式授意、指使、强令会计机构、会计人员伪造、变造会计凭证、会计账簿和其他会计资料，提供虚假财务会计报告"
                ]
            ),
        ]
        self.save_standards()

    def save_standards(self) -> None:
        with open(self.standards_file, "w", encoding="utf-8") as f:
            json.dump([asdict(standard) for standard in self.standards], f, ensure_ascii=False, indent=2)

    def add_standard(self, name: str, description: str, category: str, version: str, effective_date: str, requirements: List[str]) -> ComplianceStandard:
        standard_id = f"standard_{len(self.standards) + 1}"
        standard = ComplianceStandard(
            id=standard_id,
            name=name,
            description=description,
            category=category,
            version=version,
            effective_date=effective_date,
            requirements=requirements
        )
        self.standards.append(standard)
        self.save_standards()
        return standard

    def list_standards(self) -> List[ComplianceStandard]:
        return self.standards

    def get_standard(self, standard_id: str) -> Optional[ComplianceStandard]:
        for standard in self.standards:
            if standard.id == standard_id:
                return standard
        return None

    def remove_standard(self, standard_id: str) -> bool:
        for i, standard in enumerate(self.standards):
            if standard.id == standard_id:
                del self.standards[i]
                self.save_standards()
                return True
        return False

    def check_compliance(self, standard_id: str, evidence: Dict[str, Any]) -> ComplianceCheckResult:
        standard = self.get_standard(standard_id)
        if not standard:
            raise ValueError(f"Standard not found: {standard_id}")

        issues = []
        recommendations = []
        evidence_required = []

        # 检查每个要求
        for requirement in standard.requirements:
            # 这里简化处理，实际应该根据具体要求和提供的证据进行详细检查
            # 这里只是模拟检查过程
            if not self._check_requirement(requirement, evidence):
                issues.append(requirement)
                recommendations.append(f"确保符合要求: {requirement}")
                evidence_required.append(f"与{requirement}相关的审计证据")

        compliant = len(issues) == 0

        return ComplianceCheckResult(
            standard_id=standard.id,
            standard_name=standard.name,
            compliant=compliant,
            issues=issues,
            recommendations=recommendations,
            evidence_required=evidence_required
        )

    def _check_requirement(self, requirement: str, evidence: Dict[str, Any]) -> bool:
        # 简化的检查逻辑，实际应该根据具体要求进行详细检查
        # 这里只是模拟检查过程
        # 检查证据中是否包含与要求相关的信息
        evidence_str = json.dumps(evidence, ensure_ascii=False)
        # 简单的关键词匹配
        keywords = ["审计证据", "职业怀疑", "重大错报风险", "成本计量", "可变现净值", "会计账簿", "原始凭证"]
        for keyword in keywords:
            if keyword in requirement and keyword in evidence_str:
                return True
        # 如果没有关键词匹配，默认返回False
        return False

    def check_all_standards(self, evidence: Dict[str, Any]) -> List[ComplianceCheckResult]:
        results = []
        for standard in self.standards:
            result = self.check_compliance(standard.id, evidence)
            results.append(result)
        return results

    def check_standards_by_category(self, category: str, evidence: Dict[str, Any]) -> List[ComplianceCheckResult]:
        results = []
        for standard in self.standards:
            if standard.category == category:
                result = self.check_compliance(standard.id, evidence)
                results.append(result)
        return results
