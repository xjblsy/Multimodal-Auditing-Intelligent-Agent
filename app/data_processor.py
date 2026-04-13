from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from .config import AppConfig


@dataclass(slots=True)
class DataSource:
    id: str
    name: str
    type: str  # csv, excel, json, database
    path: str
    description: str = ""
    last_updated: str = ""


@dataclass(slots=True)
class FinancialAnalysisResult:
    metrics: Dict[str, float]
    trends: Dict[str, List[float]]
    anomalies: List[Dict[str, Any]]
    recommendations: List[str]


class DataProcessor:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.data_dir = config.data_dir / "financial"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.sources_file = self.data_dir / "sources.json"
        self.load_sources()

    def load_sources(self) -> None:
        if self.sources_file.exists():
            with open(self.sources_file, "r", encoding="utf-8") as f:
                self.sources = json.load(f)
        else:
            self.sources = {}

    def save_sources(self) -> None:
        with open(self.sources_file, "w", encoding="utf-8") as f:
            json.dump(self.sources, f, ensure_ascii=False, indent=2)

    def add_data_source(self, name: str, type: str, path: str, description: str = "") -> DataSource:
        source_id = f"source_{len(self.sources) + 1}"
        source = DataSource(
            id=source_id,
            name=name,
            type=type,
            path=path,
            description=description,
            last_updated=pd.Timestamp.now().isoformat()
        )
        # 由于使用了 slots=True，需要手动构建字典
        self.sources[source_id] = {
            "id": source.id,
            "name": source.name,
            "type": source.type,
            "path": source.path,
            "description": source.description,
            "last_updated": source.last_updated
        }
        self.save_sources()
        return source

    def list_data_sources(self) -> List[DataSource]:
        return [DataSource(**source) for source in self.sources.values()]

    def get_data_source(self, source_id: str) -> Optional[DataSource]:
        source_data = self.sources.get(source_id)
        if source_data:
            return DataSource(**source_data)
        return None

    def remove_data_source(self, source_id: str) -> bool:
        if source_id in self.sources:
            del self.sources[source_id]
            self.save_sources()
            return True
        return False

    def load_data(self, source_id: str) -> Optional[pd.DataFrame]:
        source = self.get_data_source(source_id)
        if not source:
            return None

        try:
            if source.type == "csv":
                return pd.read_csv(source.path)
            elif source.type == "excel":
                return pd.read_excel(source.path)
            elif source.type == "json":
                return pd.read_json(source.path)
            else:
                return None
        except Exception as e:
            print(f"Error loading data: {e}")
            return None

    def process_financial_data(self, df: pd.DataFrame) -> FinancialAnalysisResult:
        metrics = {}
        trends = {}
        anomalies = []
        recommendations = []

        # 计算基本财务指标
        if "revenue" in df.columns:
            metrics["total_revenue"] = float(df["revenue"].sum())
            metrics["avg_revenue"] = float(df["revenue"].mean())
            trends["revenue"] = df["revenue"].tolist()

        if "expenses" in df.columns:
            metrics["total_expenses"] = float(df["expenses"].sum())
            metrics["avg_expenses"] = float(df["expenses"].mean())
            trends["expenses"] = df["expenses"].tolist()

        if "revenue" in df.columns and "expenses" in df.columns:
            metrics["profit"] = metrics.get("total_revenue", 0) - metrics.get("total_expenses", 0)
            if metrics.get("total_revenue", 0) > 0:
                metrics["profit_margin"] = metrics["profit"] / metrics["total_revenue"] * 100

        # 识别异常
        if "revenue" in df.columns:
            revenue_mean = df["revenue"].mean()
            revenue_std = df["revenue"].std()
            for i, value in enumerate(df["revenue"]):
                if abs(value - revenue_mean) > 2 * revenue_std:
                    anomalies.append({
                        "type": "revenue_anomaly",
                        "index": i,
                        "value": float(value),
                        "expected": float(revenue_mean),
                        "deviation": float(abs(value - revenue_mean) / revenue_std)
                    })

        # 生成建议
        if metrics.get("profit", 0) < 0:
            recommendations.append("公司当前处于亏损状态，建议分析成本结构并寻找降低成本的机会。")
        elif metrics.get("profit_margin", 0) < 10:
            recommendations.append("利润率较低，建议优化定价策略或提高运营效率。")

        if trends.get("revenue"):
            revenue_trend = trends["revenue"]
            if len(revenue_trend) >= 2 and revenue_trend[-1] < revenue_trend[0]:
                recommendations.append("收入呈下降趋势，建议分析市场变化并制定增长策略。")

        return FinancialAnalysisResult(
            metrics=metrics,
            trends=trends,
            anomalies=anomalies,
            recommendations=recommendations
        )

    def analyze_data_source(self, source_id: str) -> Optional[FinancialAnalysisResult]:
        df = self.load_data(source_id)
        if df is not None:
            return self.process_financial_data(df)
        return None
