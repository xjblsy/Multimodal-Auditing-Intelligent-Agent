from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import AppConfig


@dataclass(slots=True)
class ReportTemplate:
    id: str
    name: str
    description: str
    sections: List[Dict[str, Any]]
    format: str  # html, markdown, pdf


@dataclass(slots=True)
class ReportData:
    company_name: str
    audit_period: str
    audit_date: str
    auditor: str
    financial_data: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    compliance_check: Dict[str, Any]
    findings: List[Dict[str, Any]]
    recommendations: List[str]


class ReportGenerator:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.templates_dir = config.data_dir / "report_templates"
        self.reports_dir = config.data_dir / "reports"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.load_templates()

    def load_templates(self) -> None:
        templates = []
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    template_data = json.load(f)
                    template = ReportTemplate(**template_data)
                    templates.append(template)
            except Exception as e:
                print(f"Error loading template {template_file}: {e}")

        if not templates:
            # 初始化默认模板
            default_template = ReportTemplate(
                id="template_1",
                name="标准审计报告模板",
                description="符合审计准则要求的标准审计报告模板",
                sections=[
                    {
                        "id": "header",
                        "title": "审计报告",
                        "content": "{{company_name}} - {{audit_period}}"
                    },
                    {
                        "id": "introduction",
                        "title": "一、审计概况",
                        "content": "我们对{{company_name}}{{audit_period}}的财务报表进行了审计，审计工作按照中国注册会计师审计准则的规定执行。"
                    },
                    {
                        "id": "financial_data",
                        "title": "二、财务数据分析",
                        "content": "{{financial_data_summary}}"
                    },
                    {
                        "id": "risk_assessment",
                        "title": "三、风险评估",
                        "content": "{{risk_assessment_summary}}"
                    },
                    {
                        "id": "compliance_check",
                        "title": "四、合规性检查",
                        "content": "{{compliance_check_summary}}"
                    },
                    {
                        "id": "findings",
                        "title": "五、审计发现",
                        "content": "{{findings_summary}}"
                    },
                    {
                        "id": "recommendations",
                        "title": "六、审计建议",
                        "content": "{{recommendations_summary}}"
                    },
                    {
                        "id": "conclusion",
                        "title": "七、审计结论",
                        "content": "基于审计工作，我们认为{{company_name}}{{audit_period}}的财务报表在所有重大方面符合企业会计准则的规定，公允反映了其财务状况、经营成果和现金流量。"
                    },
                    {
                        "id": "signature",
                        "title": "审计人员签名",
                        "content": "审计人员: {{auditor}}\n日期: {{audit_date}}"
                    }
                ],
                format="html"
            )
            self.save_template(default_template)
            templates.append(default_template)

        self.templates = templates

    def save_template(self, template: ReportTemplate) -> None:
        template_path = self.templates_dir / f"{template.id}.json"
        with open(template_path, "w", encoding="utf-8") as f:
            json.dump(asdict(template), f, ensure_ascii=False, indent=2)

    def add_template(self, name: str, description: str, sections: List[Dict[str, Any]], format: str) -> ReportTemplate:
        template_id = f"template_{len(self.templates) + 1}"
        template = ReportTemplate(
            id=template_id,
            name=name,
            description=description,
            sections=sections,
            format=format
        )
        self.templates.append(template)
        self.save_template(template)
        return template

    def list_templates(self) -> List[ReportTemplate]:
        return self.templates

    def get_template(self, template_id: str) -> Optional[ReportTemplate]:
        for template in self.templates:
            if template.id == template_id:
                return template
        return None

    def remove_template(self, template_id: str) -> bool:
        for i, template in enumerate(self.templates):
            if template.id == template_id:
                del self.templates[i]
                template_path = self.templates_dir / f"{template_id}.json"
                if template_path.exists():
                    template_path.unlink()
                return True
        return False

    def generate_report(self, template_id: str, report_data: ReportData) -> str:
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")

        # 生成各个部分的摘要
        financial_data_summary = self._generate_financial_summary(report_data.financial_data)
        risk_assessment_summary = self._generate_risk_summary(report_data.risk_assessment)
        compliance_check_summary = self._generate_compliance_summary(report_data.compliance_check)
        findings_summary = self._generate_findings_summary(report_data.findings)
        recommendations_summary = self._generate_recommendations_summary(report_data.recommendations)

        # 替换模板中的变量
        report_content = ""
        for section in template.sections:
            content = section["content"]
            content = content.replace("{{company_name}}", report_data.company_name)
            content = content.replace("{{audit_period}}", report_data.audit_period)
            content = content.replace("{{audit_date}}", report_data.audit_date)
            content = content.replace("{{auditor}}", report_data.auditor)
            content = content.replace("{{financial_data_summary}}", financial_data_summary)
            content = content.replace("{{risk_assessment_summary}}", risk_assessment_summary)
            content = content.replace("{{compliance_check_summary}}", compliance_check_summary)
            content = content.replace("{{findings_summary}}", findings_summary)
            content = content.replace("{{recommendations_summary}}", recommendations_summary)

            if template.format == "html":
                report_content += f"<h2>{section['title']}</h2><p>{content}</p>"
            else:
                report_content += f"## {section['title']}\n{content}\n"

        # 保存报告
        report_filename = f"{report_data.company_name}_{report_data.audit_period}_report.{template.format}"
        report_path = self.reports_dir / report_filename
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        return str(report_path)

    def _generate_financial_summary(self, financial_data: Dict[str, Any]) -> str:
        summary = ""
        if financial_data.get("metrics"):
            summary += "主要财务指标：\n"
            for key, value in financial_data["metrics"].items():
                summary += f"- {key}: {value}\n"
        if financial_data.get("anomalies"):
            summary += "\n异常情况：\n"
            for anomaly in financial_data["anomalies"]:
                summary += f"- {anomaly.get('type')}: {anomaly.get('value')}\n"
        return summary

    def _generate_risk_summary(self, risk_assessment: Dict[str, Any]) -> str:
        summary = ""
        if risk_assessment.get("overall_risk"):
            risk_level = "低"
            if risk_assessment["overall_risk"] >= 4:
                risk_level = "高"
            elif risk_assessment["overall_risk"] >= 3:
                risk_level = "中"
            summary += f"整体风险等级：{risk_level}（评分：{risk_assessment['overall_risk']}/5）\n"
        if risk_assessment.get("risk_factors"):
            summary += "\n主要风险因素：\n"
            for factor in risk_assessment["risk_factors"]:
                summary += f"- {factor.get('name')}（严重程度：{factor.get('severity')}，可能性：{factor.get('likelihood')}）\n"
        return summary

    def _generate_compliance_summary(self, compliance_check: Dict[str, Any]) -> str:
        summary = ""
        if compliance_check.get("results"):
            compliant_count = sum(1 for res in compliance_check["results"] if res.get("compliant"))
            total_count = len(compliance_check["results"])
            summary += f"合规标准检查结果：{compliant_count}/{total_count} 项合规\n"
            for res in compliance_check["results"]:
                status = "合规" if res.get("compliant") else "不合规"
                summary += f"- {res.get('standard_name')}：{status}\n"
        return summary

    def _generate_findings_summary(self, findings: List[Dict[str, Any]]) -> str:
        if not findings:
            return "未发现重大问题。"
        summary = ""
        for finding in findings:
            summary += f"- {finding.get('title')}: {finding.get('description')}\n"
        return summary

    def _generate_recommendations_summary(self, recommendations: List[str]) -> str:
        if not recommendations:
            return "无特殊建议。"
        summary = ""
        for i, recommendation in enumerate(recommendations, 1):
            summary += f"{i}. {recommendation}\n"
        return summary
