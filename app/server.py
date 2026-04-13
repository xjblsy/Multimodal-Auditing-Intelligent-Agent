from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .agent import AuditCoach
from .config import AppConfig, build_config
from .compliance_checker import ComplianceChecker
from .data_processor import DataProcessor
from .kb import KnowledgeBase
from .llm import build_provider
from .profile import load_profile
from .report_generator import ReportData, ReportGenerator
from .risk_assessor import RiskAssessor


def build_app() -> tuple[AppConfig, KnowledgeBase, AuditCoach, DataProcessor, RiskAssessor, ComplianceChecker, ReportGenerator]:
    config = build_config()
    kb = KnowledgeBase(config)
    profile = load_profile(config)
    coach = AuditCoach(config, kb, build_provider(config), profile)
    data_processor = DataProcessor(config)
    risk_assessor = RiskAssessor(config, data_processor)
    compliance_checker = ComplianceChecker(config)
    report_generator = ReportGenerator(config)
    return config, kb, coach, data_processor, risk_assessor, compliance_checker, report_generator


class AuditRequestHandler(BaseHTTPRequestHandler):
    server_version = "AuditCoach/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/health":
            self._json({"status": "ok"})
            return

        if path == "/api/config":
            config = self.server.app_config
            self._json(
                {
                    "default_industry": config.default_industry,
                    "model_provider": config.model_provider,
                    "model_name": config.model_name,
                    "provider_ready": bool(config.api_key),
                    "doc_model_name": config.doc_model_name,
                    "vision_model_name": config.vision_model_name,
                    "remote_import_enabled": config.enable_remote_import,
                }
            )
            return

        if path == "/api/profile":
            self._json(self.server.coach.profile.raw)
            return

        if path == "/api/knowledge":
            query = parse_qs(parsed.query)
            items = self.server.kb.search(
                query=query.get("query", [""])[0],
                industry=query.get("industry", [""])[0],
                tags=[tag for tag in query.get("tag", []) if tag],
                limit=int(query.get("limit", ["10"])[0]),
            )
            self._json({"items": items})
            return

        if path.startswith("/api/knowledge/"):
            item_id = path.split("/")[-1]
            item = self.server.kb.get_item(item_id)
            if not item:
                self._json({"error": "Knowledge item not found"}, status=HTTPStatus.NOT_FOUND)
                return
            self._json(item)
            return

        if path == "/api/scenarios":
            self._json({"items": self.server.kb.list_scenarios()})
            return

        if path.startswith("/api/scenarios/"):
            scenario_id = path.split("/")[-1]
            scenario = self.server.kb.get_scenario(scenario_id)
            if not scenario:
                self._json({"error": "Scenario not found"}, status=HTTPStatus.NOT_FOUND)
                return
            self._json(scenario)
            return

        if path == "/api/data-sources":
            sources = self.server.data_processor.list_data_sources()
            self._json({"items": [source.__dict__ for source in sources]})
            return

        if path.startswith("/api/data-sources/"):
            source_id = path.split("/")[-1]
            source = self.server.data_processor.get_data_source(source_id)
            if not source:
                self._json({"error": "Data source not found"}, status=HTTPStatus.NOT_FOUND)
                return
            self._json(source.__dict__)
            return

        if path == "/api/risk-factors":
            factors = self.server.risk_assessor.list_risk_factors()
            self._json({"items": [factor.__dict__ for factor in factors]})
            return

        if path.startswith("/api/risk-factors/"):
            risk_id = path.split("/")[-1]
            factor = self.server.risk_assessor.get_risk_factor(risk_id)
            if not factor:
                self._json({"error": "Risk factor not found"}, status=HTTPStatus.NOT_FOUND)
                return
            self._json(factor.__dict__)
            return

        if path == "/api/compliance-standards":
            standards = self.server.compliance_checker.list_standards()
            self._json({"items": [standard.__dict__ for standard in standards]})
            return

        if path.startswith("/api/compliance-standards/"):
            standard_id = path.split("/")[-1]
            standard = self.server.compliance_checker.get_standard(standard_id)
            if not standard:
                self._json({"error": "Compliance standard not found"}, status=HTTPStatus.NOT_FOUND)
                return
            self._json(standard.__dict__)
            return

        if path == "/api/report-templates":
            templates = self.server.report_generator.list_templates()
            self._json({"items": [template.__dict__ for template in templates]})
            return

        if path.startswith("/api/report-templates/"):
            template_id = path.split("/")[-1]
            template = self.server.report_generator.get_template(template_id)
            if not template:
                self._json({"error": "Report template not found"}, status=HTTPStatus.NOT_FOUND)
                return
            self._json(template.__dict__)
            return

        if path.startswith("/media/"):
            relative = path.removeprefix("/media/")
            self._serve_file(self.server.app_config.media_dir / relative)
            return

        if path in {"/", "/index.html"}:
            self._serve_file(self.server.app_config.web_dir / "index.html")
            return

        candidate = self.server.app_config.web_dir / path.lstrip("/")
        if candidate.exists() and candidate.is_file():
            self._serve_file(candidate)
            return

        self._json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        payload = self._body_json()

        if path == "/api/chat":
            result = self.server.coach.answer_query(
                query=payload.get("query", ""),
                industry=payload.get("industry", ""),
                tags=payload.get("tags", []),
                scenario_id=payload.get("scenario_id"),
            )
            self._json(result)
            return

        if path == "/api/learning-path":
            result = self.server.coach.build_learning_path(
                industry=payload.get("industry") or self.server.app_config.default_industry,
                role=payload.get("role") or "助理审计员",
                target_level=payload.get("target_level") or "中级",
            )
            self._json(result)
            return

        if path == "/api/rebuild-index":
            result = self.server.kb.rebuild_index()
            self._json({"status": "rebuilt", **result})
            return

        if path == "/api/knowledge":
            item = self.server.kb.upsert_item(payload)
            self._json(item, status=HTTPStatus.CREATED)
            return

        if path == "/api/data-sources":
            source = self.server.data_processor.add_data_source(
                name=payload.get("name", ""),
                type=payload.get("type", ""),
                path=payload.get("path", ""),
                description=payload.get("description", "")
            )
            self._json(source.__dict__, status=HTTPStatus.CREATED)
            return

        if path.startswith("/api/data-sources/") and path.endswith("/analyze"):
            source_id = path.split("/")[-2]
            result = self.server.data_processor.analyze_data_source(source_id)
            if result:
                self._json({
                    "metrics": result.metrics,
                    "trends": result.trends,
                    "anomalies": result.anomalies,
                    "recommendations": result.recommendations
                })
            else:
                self._json({"error": "Failed to analyze data source"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if path == "/api/risk-factors":
            factor = self.server.risk_assessor.add_risk_factor(
                name=payload.get("name", ""),
                description=payload.get("description", ""),
                severity=int(payload.get("severity", 3)),
                likelihood=int(payload.get("likelihood", 3)),
                category=payload.get("category", ""),
                industry=payload.get("industry", "通用"),
                controls=payload.get("controls", [])
            )
            self._json(factor.__dict__, status=HTTPStatus.CREATED)
            return

        if path == "/api/risk-assessment":
            assessment = self.server.risk_assessor.assess_risk(
                industry=payload.get("industry", "通用"),
                data_source_id=payload.get("data_source_id")
            )
            self._json({
                "overall_risk": assessment.overall_risk,
                "risk_factors": [factor.__dict__ for factor in assessment.risk_factors],
                "recommendations": assessment.recommendations,
                "industry_specific_risks": assessment.industry_specific_risks
            })
            return

        if path == "/api/compliance-standards":
            standard = self.server.compliance_checker.add_standard(
                name=payload.get("name", ""),
                description=payload.get("description", ""),
                category=payload.get("category", "审计准则"),
                version=payload.get("version", ""),
                effective_date=payload.get("effective_date", ""),
                requirements=payload.get("requirements", [])
            )
            self._json(standard.__dict__, status=HTTPStatus.CREATED)
            return

        if path == "/api/compliance-check":
            standard_id = payload.get("standard_id")
            if standard_id:
                result = self.server.compliance_checker.check_compliance(
                    standard_id=standard_id,
                    evidence=payload.get("evidence", {})
                )
                self._json({
                    "standard_id": result.standard_id,
                    "standard_name": result.standard_name,
                    "compliant": result.compliant,
                    "issues": result.issues,
                    "recommendations": result.recommendations,
                    "evidence_required": result.evidence_required
                })
            else:
                results = self.server.compliance_checker.check_all_standards(
                    evidence=payload.get("evidence", {})
                )
                self._json({
                    "results": [
                        {
                            "standard_id": result.standard_id,
                            "standard_name": result.standard_name,
                            "compliant": result.compliant,
                            "issues": result.issues,
                            "recommendations": result.recommendations,
                            "evidence_required": result.evidence_required
                        }
                        for result in results
                    ]
                })
            return

        if path == "/api/report-templates":
            template = self.server.report_generator.add_template(
                name=payload.get("name", ""),
                description=payload.get("description", ""),
                sections=payload.get("sections", []),
                format=payload.get("format", "html")
            )
            self._json(template.__dict__, status=HTTPStatus.CREATED)
            return

        if path == "/api/generate-report":
            template_id = payload.get("template_id")
            report_data = ReportData(
                company_name=payload.get("company_name", ""),
                audit_period=payload.get("audit_period", ""),
                audit_date=payload.get("audit_date", ""),
                auditor=payload.get("auditor", ""),
                financial_data=payload.get("financial_data", {}),
                risk_assessment=payload.get("risk_assessment", {}),
                compliance_check=payload.get("compliance_check", {}),
                findings=payload.get("findings", []),
                recommendations=payload.get("recommendations", [])
            )
            try:
                report_path = self.server.report_generator.generate_report(template_id, report_data)
                self._json({"report_path": report_path})
            except Exception as e:
                self._json({"error": str(e)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if path.startswith("/api/scenarios/") and path.endswith("/evaluate"):
            parts = [part for part in path.split("/") if part]
            scenario_id = parts[2]
            result = self.server.coach.evaluate_scenario(
                scenario_id=scenario_id,
                stage_id=payload.get("stage_id", ""),
                answer=payload.get("answer", ""),
            )
            self._json(result)
            return

        self._json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_PUT(self) -> None:
        path = urlparse(self.path).path
        payload = self._body_json()
        if path.startswith("/api/knowledge/"):
            item_id = path.split("/")[-1]
            payload["id"] = item_id
            item = self.server.kb.upsert_item(payload)
            self._json(item)
            return
        self._json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_DELETE(self) -> None:
        path = urlparse(self.path).path
        if path.startswith("/api/knowledge/"):
            item_id = path.split("/")[-1]
            deleted = self.server.kb.delete_item(item_id)
            if not deleted:
                self._json({"error": "Knowledge item not found"}, status=HTTPStatus.NOT_FOUND)
                return
            self._json({"status": "deleted", "id": item_id})
            return
        if path.startswith("/api/data-sources/"):
            source_id = path.split("/")[-1]
            deleted = self.server.data_processor.remove_data_source(source_id)
            if not deleted:
                self._json({"error": "Data source not found"}, status=HTTPStatus.NOT_FOUND)
                return
            self._json({"status": "deleted", "id": source_id})
            return
        if path.startswith("/api/risk-factors/"):
            risk_id = path.split("/")[-1]
            deleted = self.server.risk_assessor.remove_risk_factor(risk_id)
            if not deleted:
                self._json({"error": "Risk factor not found"}, status=HTTPStatus.NOT_FOUND)
                return
            self._json({"status": "deleted", "id": risk_id})
            return
        if path.startswith("/api/compliance-standards/"):
            standard_id = path.split("/")[-1]
            deleted = self.server.compliance_checker.remove_standard(standard_id)
            if not deleted:
                self._json({"error": "Compliance standard not found"}, status=HTTPStatus.NOT_FOUND)
                return
            self._json({"status": "deleted", "id": standard_id})
            return
        if path.startswith("/api/report-templates/"):
            template_id = path.split("/")[-1]
            deleted = self.server.report_generator.remove_template(template_id)
            if not deleted:
                self._json({"error": "Report template not found"}, status=HTTPStatus.NOT_FOUND)
                return
            self._json({"status": "deleted", "id": template_id})
            return
        self._json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def _body_json(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def _json(self, payload: dict[str, object], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self._json({"error": "File not found"}, status=HTTPStatus.NOT_FOUND)
            return

        content = path.read_bytes()
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        if content_type.startswith("text/") or content_type in {
            "application/javascript",
            "application/json",
            "application/xml",
            "image/svg+xml",
        }:
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        else:
            self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format: str, *args: object) -> None:
        return


def run_server(host: str | None = None, port: int | None = None) -> None:
    config, kb, coach, data_processor, risk_assessor, compliance_checker, report_generator = build_app()
    server = ThreadingHTTPServer((host or config.host, port or config.port), AuditRequestHandler)
    server.app_config = config
    server.kb = kb
    server.coach = coach
    server.data_processor = data_processor
    server.risk_assessor = risk_assessor
    server.compliance_checker = compliance_checker
    server.report_generator = report_generator
    print(f"Audit coach is running on http://{host or config.host}:{port or config.port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
