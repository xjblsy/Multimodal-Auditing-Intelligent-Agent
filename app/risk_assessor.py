from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import AppConfig
from .data_processor import DataProcessor


@dataclass(slots=True)
class RiskFactor:
    id: str
    name: str
    description: str
    severity: int  # 1-5, 5 is highest
    likelihood: int  # 1-5, 5 is highest
    category: str
    industry: str
    controls: List[str]


@dataclass(slots=True)
class RiskAssessment:
    overall_risk: int  # 1-5, 5 is highest
    risk_factors: List[RiskFactor]
    recommendations: List[str]
    industry_specific_risks: List[str]


class RiskAssessor:
    def __init__(self, config: AppConfig, data_processor: DataProcessor) -> None:
        self.config = config
        self.data_processor = data_processor
        self.risk_factors_file = config.data_dir / "risk_factors.json"
        self.load_risk_factors()

    def load_risk_factors(self) -> None:
        if self.risk_factors_file.exists():
            try:
                with open(self.risk_factors_file, "r", encoding="utf-8") as f:
                    risk_data = json.load(f)
                    self.risk_factors = [RiskFactor(**factor) for factor in risk_data]
            except (json.JSONDecodeError, ValueError):
                # 文件格式不正确，使用默认风险因素
                self._initialize_default_risks()
        else:
            # 文件不存在，使用默认风险因素
            self._initialize_default_risks()
    
    def _initialize_default_risks(self) -> None:
        # 初始化默认风险因素
        self.risk_factors = [
            RiskFactor(
                id="risk_1",
                name="收入确认风险",
                description="企业可能提前确认收入或虚构收入",
                severity=5,
                likelihood=4,
                category="收入循环",
                industry="通用",
                controls=["检查销售合同条款", "验证发货记录", "检查应收账款回款情况"]
            ),
            RiskFactor(
                id="risk_2",
                name="存货估值风险",
                description="企业可能高估存货价值或虚构存货",
                severity=4,
                likelihood=3,
                category="存货循环",
                industry="制造业",
                controls=["执行存货监盘", "检查存货计价方法", "分析存货周转率"]
            ),
            RiskFactor(
                id="risk_3",
                name="费用资本化风险",
                description="企业可能将应费用化的支出资本化",
                severity=4,
                likelihood=3,
                category="费用循环",
                industry="通用",
                controls=["检查资本化政策", "验证资本化条件", "分析资本化资产的摊销"]
            ),
            RiskFactor(
                id="risk_4",
                name="关联交易风险",
                description="企业可能通过关联交易操纵利润",
                severity=5,
                likelihood=3,
                category="关联交易",
                industry="通用",
                controls=["识别关联方", "检查关联交易定价", "验证关联交易的必要性"]
            ),
            RiskFactor(
                id="risk_5",
                name="货币资金风险",
                description="企业可能存在货币资金挪用或虚构",
                severity=5,
                likelihood=2,
                category="货币资金",
                industry="通用",
                controls=["执行银行函证", "检查银行对账单", "分析银行余额调节表"]
            ),
        ]
        self.save_risk_factors()

    def save_risk_factors(self) -> None:
        with open(self.risk_factors_file, "w", encoding="utf-8") as f:
            json.dump([asdict(factor) for factor in self.risk_factors], f, ensure_ascii=False, indent=2)

    def add_risk_factor(self, name: str, description: str, severity: int, likelihood: int, category: str, industry: str, controls: List[str]) -> RiskFactor:
        risk_id = f"risk_{len(self.risk_factors) + 1}"
        risk_factor = RiskFactor(
            id=risk_id,
            name=name,
            description=description,
            severity=severity,
            likelihood=likelihood,
            category=category,
            industry=industry,
            controls=controls
        )
        self.risk_factors.append(risk_factor)
        self.save_risk_factors()
        return risk_factor

    def list_risk_factors(self) -> List[RiskFactor]:
        return self.risk_factors

    def get_risk_factor(self, risk_id: str) -> Optional[RiskFactor]:
        for factor in self.risk_factors:
            if factor.id == risk_id:
                return factor
        return None

    def remove_risk_factor(self, risk_id: str) -> bool:
        for i, factor in enumerate(self.risk_factors):
            if factor.id == risk_id:
                del self.risk_factors[i]
                self.save_risk_factors()
                return True
        return False

    def assess_risk(self, industry: str, data_source_id: Optional[str] = None) -> RiskAssessment:
        # 筛选与行业相关的风险因素
        relevant_risks = [
            factor for factor in self.risk_factors 
            if factor.industry == industry or factor.industry == "通用"
        ]

        # 如果提供了数据源，结合财务数据分析调整风险评估
        if data_source_id:
            analysis_result = self.data_processor.analyze_data_source(data_source_id)
            if analysis_result:
                # 根据财务数据分析结果调整风险评估
                relevant_risks = self._adjust_risks_based_on_data(relevant_risks, analysis_result)

        # 计算整体风险评分
        if relevant_risks:
            overall_risk = sum(factor.severity * factor.likelihood for factor in relevant_risks) // len(relevant_risks)
            overall_risk = min(max(overall_risk, 1), 5)  # 确保在1-5范围内
        else:
            overall_risk = 2  # 默认中等风险

        # 生成建议
        recommendations = self._generate_recommendations(relevant_risks, industry)

        # 提取行业特定风险
        industry_specific_risks = [
            factor.name for factor in relevant_risks if factor.industry == industry
        ]

        return RiskAssessment(
            overall_risk=overall_risk,
            risk_factors=relevant_risks,
            recommendations=recommendations,
            industry_specific_risks=industry_specific_risks
        )

    def _adjust_risks_based_on_data(self, risks: List[RiskFactor], analysis_result: Any) -> List[RiskFactor]:
        # 根据财务数据分析结果调整风险评估
        adjusted_risks = []
        for risk in risks:
            adjusted_risk = RiskFactor(**asdict(risk))
            
            # 根据财务指标调整风险
            if analysis_result.anomalies:
                # 如果有异常，增加风险
                adjusted_risk.likelihood = min(adjusted_risk.likelihood + 1, 5)
            
            if analysis_result.metrics:
                # 根据财务指标调整风险
                if risk.name == "收入确认风险" and "revenue" in analysis_result.metrics:
                    # 收入异常波动可能增加收入确认风险
                    if analysis_result.trends and "revenue" in analysis_result.trends:
                        revenue_trend = analysis_result.trends["revenue"]
                        if len(revenue_trend) >= 2 and abs(revenue_trend[-1] - revenue_trend[0]) / revenue_trend[0] > 0.5:
                            adjusted_risk.likelihood = min(adjusted_risk.likelihood + 1, 5)
                
                if risk.name == "存货估值风险" and "inventory" in analysis_result.metrics:
                    # 存货异常可能增加存货估值风险
                    adjusted_risk.likelihood = min(adjusted_risk.likelihood + 1, 5)
            
            adjusted_risks.append(adjusted_risk)
        return adjusted_risks

    def _generate_recommendations(self, risks: List[RiskFactor], industry: str) -> List[str]:
        recommendations = []
        
        # 按风险类别分组
        category_risks = {}
        for risk in risks:
            if risk.category not in category_risks:
                category_risks[risk.category] = []
            category_risks[risk.category].append(risk)
        
        # 为每个类别生成建议
        for category, category_risk_list in category_risks.items():
            high_risk_factors = [risk for risk in category_risk_list if risk.severity >= 4]
            if high_risk_factors:
                recommendations.append(f"对于{category}，重点关注以下高风险领域：{', '.join([risk.name for risk in high_risk_factors])}")
                # 添加具体控制措施
                for risk in high_risk_factors:
                    if risk.controls:
                        recommendations.append(f"针对{risk.name}，建议实施以下控制：{', '.join(risk.controls[:3])}")
        
        # 添加行业特定建议
        if industry != "通用":
            industry_risks = [risk for risk in risks if risk.industry == industry]
            if industry_risks:
                recommendations.append(f"{industry}行业特有风险：{', '.join([risk.name for risk in industry_risks])}")
        
        # 添加总体建议
        if any(risk.severity >= 4 for risk in risks):
            recommendations.append("建议增加审计程序的范围和深度，特别是对高风险领域的测试。")
        
        return recommendations
