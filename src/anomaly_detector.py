"""
异常检测模块：多维度KPI异常检测 + AI归因分析
"""
import pandas as pd
import numpy as np
from typing import Any


class AnomalyDetector:
    """KPI异常检测器"""

    def __init__(self, threshold: float = 0.15):
        """
        threshold: 异常判定阈值（波动超过此比例视为异常），默认15%
        """
        self.threshold = threshold
        self.anomalies = []

    def detect_revenue_anomaly(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        """检测收入达成率异常"""
        anomalies = []

        # 按区域+产品线分组比较
        for (region, product), group in df.groupby(["region", "product_line"]):
            group = group.sort_values("month")
            if len(group) < 2:
                continue

            # 环比检测
            for i in range(1, len(group)):
                current = group.iloc[i]
                previous = group.iloc[i - 1]
                mom_change = (current["revenue"] - previous["revenue"]) / previous["revenue"]

                if abs(mom_change) > self.threshold:
                    direction = "上升" if mom_change > 0 else "下降"
                    anomalies.append({
                        "类型": "收入环比异常",
                        "区域": region,
                        "产品线": product,
                        "月份": int(current["month"]),
                        "当前收入": int(current["revenue"]),
                        "上月收入": int(previous["revenue"]),
                        "环比变化": f"{mom_change:.1%}",
                        "方向": direction,
                        "严重程度": "⚠️ 高" if abs(mom_change) > 0.25 else "⚡ 中"
                    })

            # 达成率检测
            for _, row in group.iterrows():
                if row["revenue_achievement"] < 85:
                    anomalies.append({
                        "类型": "收入达成率偏低",
                        "区域": region,
                        "产品线": product,
                        "月份": int(row["month"]),
                        "实际达成率": f"{row['revenue_achievement']:.1f}%",
                        "目标收入": int(row["revenue_target"]),
                        "实际收入": int(row["revenue"]),
                        "方向": "不达标",
                        "严重程度": "🚨 严重" if row["revenue_achievement"] < 75 else "⚠️ 高"
                    })

        return anomalies

    def detect_margin_anomaly(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        """检测毛利率异常"""
        anomalies = []

        for (region, product), group in df.groupby(["region", "product_line"]):
            group = group.sort_values("month")
            avg_margin = group["gross_margin"].mean()

            for _, row in group.iterrows():
                deviation = row["gross_margin"] - avg_margin
                if abs(deviation) > 5:  # 偏差超过5个百分点
                    direction = "高于均值" if deviation > 0 else "低于均值"
                    anomalies.append({
                        "类型": "毛利率异常波动",
                        "区域": region,
                        "产品线": product,
                        "月份": int(row["month"]),
                        "当月毛利率": f"{row['gross_margin']:.1f}%",
                        "历史均价": f"{avg_margin:.1f}%",
                        "偏离幅度": f"{deviation:+.1f}pp",
                        "方向": direction,
                        "严重程度": "🚨 严重" if abs(deviation) > 8 else "⚠️ 高"
                    })

        return anomalies

    def detect_operations_anomaly(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        """检测运营指标异常"""
        anomalies = []

        # 库存周转率过低检测
        if "inventory_turnover" in df.columns:
            for _, row in df.iterrows():
                if row["inventory_turnover"] < 3.5:
                    anomalies.append({
                        "类型": "库存周转率偏低",
                        "区域": row["region"],
                        "产品线": row["product_line"],
                        "月份": int(row["month"]),
                        "库存周转率": f"{row['inventory_turnover']:.1f}",
                        "方向": "偏低",
                        "严重程度": "⚠️ 高" if row["inventory_turnover"] < 3.0 else "⚡ 中"
                    })

        # 应收账款天数过长
        if "accounts_receivable_days" in df.columns:
            for _, row in df.iterrows():
                if row["accounts_receivable_days"] > 45:
                    anomalies.append({
                        "类型": "应收账款周期过长",
                        "区域": row["region"],
                        "产品线": row["product_line"],
                        "月份": int(row["month"]),
                        "应收账款天数": f"{row['accounts_receivable_days']:.0f}天",
                        "方向": "偏高",
                        "严重程度": "🚨 严重" if row["accounts_receivable_days"] > 50 else "⚠️ 高"
                    })

        # 退货率过高
        if "return_rate" in df.columns:
            for _, row in df.iterrows():
                if row["return_rate"] > 0.035:
                    anomalies.append({
                        "类型": "退货率偏高",
                        "区域": row["region"],
                        "产品线": row["product_line"],
                        "月份": int(row["month"]),
                        "退货率": f"{row['return_rate']:.1%}",
                        "方向": "偏高",
                        "严重程度": "⚠️ 高"
                    })

        return anomalies

    def detect_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """综合异常检测"""
        all_anomalies = []
        all_anomalies.extend(self.detect_revenue_anomaly(df))
        all_anomalies.extend(self.detect_margin_anomaly(df))
        all_anomalies.extend(self.detect_operations_anomaly(df))

        self.anomalies = all_anomalies
        result_df = pd.DataFrame(all_anomalies)
        if not result_df.empty:
            result_df = result_df.sort_values("严重程度", ascending=False)

        anomaly_count = len(all_anomalies)
        print(f"🔍 异常检测完成：发现 {anomaly_count} 个异常点")
        return result_df

    def get_anomaly_summary(self) -> str:
        """生成异常摘要，供AI分析使用"""
        if not self.anomalies:
            return "未发现显著异常，各项经营指标运行平稳。"

        by_type = {}
        for a in self.anomalies:
            t = a["类型"]
            by_type[t] = by_type.get(t, 0) + 1

        lines = ["## 📊 KPI异常检测摘要\n"]
        lines.append(f"共发现 **{len(self.anomalies)}** 个异常点：\n")
        for t, count in by_type.items():
            lines.append(f"- {t}：{count} 项")

        lines.append("\n### 🔴 重点关注\n")
        severe = [a for a in self.anomalies if "严重" in a.get("严重程度", "")]
        for s in severe[:5]:
            lines.append(
                f"- 【{s['区域']}】{s['产品线']} {s['月份']}月 | "
                f"{s['类型']} | {s.get('方向', '')} | {s['严重程度']}"
            )

        return "\n".join(lines)
