"""
可视化模块：交互式图表生成
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd


class Visualizer:
    """数据可视化引擎"""

    @staticmethod
    def revenue_by_region(df: pd.DataFrame) -> go.Figure:
        """各区域收入对比柱状图"""
        summary = df.groupby("region")["revenue"].sum().reset_index()
        fig = px.bar(
            summary, x="region", y="revenue",
            title="各区域累计收入对比",
            color="region",
            text_auto=".2s",
            labels={"revenue": "收入（元）", "region": "区域"}
        )
        fig.update_layout(showlegend=False, height=400)
        return fig

    @staticmethod
    def monthly_trend(df: pd.DataFrame) -> go.Figure:
        """月度收入与毛利率趋势"""
        monthly = df.groupby("month").agg(
            收入=("revenue", "sum"),
            毛利率=("gross_margin", "mean")
        ).reset_index()

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Bar(x=monthly["month"], y=monthly["收入"], name="总收入",
                   marker_color="steelblue"),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(x=monthly["month"], y=monthly["毛利率"], name="毛利率(%)",
                       mode="lines+markers", line=dict(color="crimson", width=3),
                       marker=dict(size=8)),
            secondary_y=True
        )

        fig.update_xaxes(title_text="月份")
        fig.update_yaxes(title_text="收入（元）", secondary_y=False)
        fig.update_yaxes(title_text="毛利率（%）", secondary_y=True)
        fig.update_layout(title="月度收入与毛利率趋势", height=400, hovermode="x unified")
        return fig

    @staticmethod
    def margin_by_product(df: pd.DataFrame) -> go.Figure:
        """各产品线毛利率对比"""
        summary = df.groupby(["region", "product_line"])["gross_margin"].mean().reset_index()
        fig = px.bar(
            summary, x="region", y="gross_margin", color="product_line",
            barmode="group",
            title="各区域 × 产品线 平均毛利率对比",
            labels={"gross_margin": "毛利率(%)", "region": "区域"}
        )
        fig.update_layout(height=400)
        return fig

    @staticmethod
    def achievement_gauge(df: pd.DataFrame) -> go.Figure:
        """收入达成率仪表盘"""
        achievement = (df["revenue"].sum() / df["revenue_target"].sum() * 100)
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=achievement,
            title={"text": "整体收入达成率"},
            delta={"reference": 100, "increasing": {"color": "green"}},
            gauge={
                "axis": {"range": [0, 120]},
                "bar": {"color": "steelblue"},
                "steps": [
                    {"range": [0, 85], "color": "lightcoral"},
                    {"range": [85, 100], "color": "lightyellow"},
                    {"range": [100, 120], "color": "lightgreen"}
                ],
                "threshold": {
                    "line": {"color": "red", "width": 3},
                    "thickness": 0.75,
                    "value": 100
                }
            }
        ))
        fig.update_layout(height=350)
        return fig

    @staticmethod
    def anomaly_heatmap(anomaly_df: pd.DataFrame, full_df: pd.DataFrame) -> go.Figure:
        """异常热力图"""
        if anomaly_df.empty:
            fig = go.Figure()
            fig.add_annotation(text="✅ 未检测到异常", showarrow=False, font=dict(size=20))
            fig.update_layout(height=350)
            return fig

        # 构建热力图数据：区域×月份的收入偏差
        pivot = full_df.pivot_table(
            values="gross_margin", index="region", columns="month", aggfunc="mean"
        )

        fig = px.imshow(
            pivot,
            text_auto=".1f",
            aspect="auto",
            color_continuous_scale="RdYlGn",
            title="各区域×月份 毛利率热力图"
        )
        fig.update_layout(height=400)
        return fig

    @staticmethod
    def operations_radar(df: pd.DataFrame) -> go.Figure:
        """运营指标雷达图"""
        ops_cols = [c for c in ["inventory_turnover", "delivery_ontime_rate", "return_rate"] if c in df.columns]
        if len(ops_cols) < 2:
            fig = go.Figure()
            fig.add_annotation(text="⚠️ 运营数据不足，无法生成雷达图", showarrow=False, font=dict(size=16))
            fig.update_layout(height=350)
            return fig

        agg_dict = {}
        if "inventory_turnover" in df.columns:
            agg_dict["库存周转"] = ("inventory_turnover", "mean")
        if "delivery_ontime_rate" in df.columns:
            agg_dict["交付及时率"] = ("delivery_ontime_rate", "mean")
        if "return_rate" in df.columns:
            agg_dict["退货率"] = ("return_rate", "mean")

        metrics = df.groupby("region").agg(**agg_dict).reset_index()

        categories = list(agg_dict.keys())
        if "退货率" in categories:
            categories[categories.index("退货率")] = "退货率(反向)"

        fig = go.Figure()

        for _, row in metrics.iterrows():
            values = []
            for cat in categories:
                if cat == "退货率(反向)":
                    values.append((1 - row["退货率"]) * 100)
                elif cat == "库存周转":
                    values.append(row["库存周转"] / 6 * 100)
                elif cat == "交付及时率":
                    values.append(row["交付及时率"] * 100)
            fig.add_trace(go.Scatterpolar(
                r=values, theta=categories, fill="toself", name=row["region"]
            ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title="各区域运营健康度雷达图",
            height=450
        )
        return fig

    @staticmethod
    def kpi_table_html(df: pd.DataFrame) -> str:
        """生成KPI汇总HTML表格"""
        total_revenue = df["revenue"].sum()
        total_cost = df["cost"].sum()
        avg_margin = ((total_revenue - total_cost) / total_revenue * 100)
        avg_achievement = (df["revenue"].sum() / df["revenue_target"].sum() * 100)

        html = f"""
        <table style="width:100%; border-collapse:collapse; font-family: sans-serif;">
        <tr style="background: #1a5276; color: white;">
            <th style="padding:10px;">指标</th><th style="padding:10px;">数值</th><th style="padding:10px;">状态</th>
        </tr>
        <tr><td style="padding:8px; border-bottom:1px solid #ddd;">累计总收入</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">¥{total_revenue:,.0f}</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{'🟢 达标' if avg_achievement >= 100 else '🟡 接近达标' if avg_achievement >= 85 else '🔴 未达标'}</td></tr>
        <tr><td style="padding:8px; border-bottom:1px solid #ddd;">累计总成本</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">¥{total_cost:,.0f}</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">-</td></tr>
        <tr><td style="padding:8px; border-bottom:1px solid #ddd;">平均毛利率</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{avg_margin:.1f}%</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{'🟢 健康' if avg_margin > 40 else '🟡 关注'}</td></tr>
        <tr><td style="padding:8px; border-bottom:1px solid #ddd;">收入达成率</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{avg_achievement:.1f}%</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{'🟢' if avg_achievement >= 100 else '🔴' if avg_achievement < 85 else '🟡'}</td></tr>
        </table>
        """
        return html
