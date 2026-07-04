"""
数据处理模块：数据加载、清洗、KPI计算
"""
import pandas as pd
import numpy as np
from pathlib import Path


class DataProcessor:
    """企业经营数据处理器"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.revenue_df = None
        self.operations_df = None
        self.merged_df = None
        self.kpi_summary = None

    def load_data(self) -> dict:
        """加载所有数据文件"""
        result = {"success": True, "messages": [], "errors": []}

        revenue_path = self.data_dir / "revenue_data.csv"
        operations_path = self.data_dir / "operations_data.csv"

        try:
            self.revenue_df = pd.read_csv(revenue_path)
            self.revenue_df["date"] = pd.to_datetime(self.revenue_df["date"])
            self.revenue_df["month"] = self.revenue_df["date"].dt.month
            msg = f"✅ 收入数据加载成功：{len(self.revenue_df)} 条记录"
            result["messages"].append(msg)
            print(msg)
        except Exception as e:
            err = f"❌ 收入数据加载失败：{e}"
            result["errors"].append(err)
            print(err)

        try:
            self.operations_df = pd.read_csv(operations_path)
            self.operations_df["date"] = pd.to_datetime(self.operations_df["date"])
            self.operations_df["month"] = self.operations_df["date"].dt.month
            msg = f"✅ 运营数据加载成功：{len(self.operations_df)} 条记录"
            result["messages"].append(msg)
            print(msg)
        except Exception as e:
            err = f"❌ 运营数据加载失败：{e}"
            result["errors"].append(err)
            print(err)

        return result

    def clean_data(self) -> dict:
        """数据清洗：缺失值、异常值处理"""
        result = {"cleaned": True, "details": []}

        if self.revenue_df is not None:
            before = len(self.revenue_df)
            self.revenue_df = self.revenue_df.dropna()
            after = len(self.revenue_df)
            if before != after:
                result["details"].append(f"收入数据删除 {before - after} 条空值记录")

        if self.operations_df is not None:
            before = len(self.operations_df)
            self.operations_df = self.operations_df.dropna()
            after = len(self.operations_df)
            if before != after:
                result["details"].append(f"运营数据删除 {before - after} 条空值记录")

        if not result["details"]:
            result["details"].append("数据无缺失值，无需清洗")
        return result

    def merge_data(self) -> pd.DataFrame:
        """合并收入与运营数据"""
        if self.revenue_df is None:
            raise ValueError("收入数据未加载，无法合并")

        if self.operations_df is not None:
            self.merged_df = pd.merge(
                self.revenue_df,
                self.operations_df,
                on=["date", "region", "product_line"],
                how="inner",
                suffixes=("", "_ops")
            )
            print(f"✅ 数据合并完成：{len(self.merged_df)} 条记录")
        else:
            # 无运营数据时，仅使用收入数据
            self.merged_df = self.revenue_df.copy()
            print("⚠️ 运营数据未加载，仅使用收入数据进行KPI计算")
        return self.merged_df

    def calculate_kpi(self) -> pd.DataFrame:
        """计算核心KPI指标"""
        if self.merged_df is None:
            self.merge_data()

        df = self.merged_df.copy()

        # 毛利率
        df["gross_margin"] = ((df["revenue"] - df["cost"]) / df["revenue"] * 100).round(2)

        # 收入达成率
        df["revenue_achievement"] = (df["revenue"] / df["revenue_target"] * 100).round(2)

        # 单位收入
        df["unit_revenue"] = (df["revenue"] / df["quantity"]).round(2)

        # 单位成本
        df["unit_cost"] = (df["cost"] / df["quantity"]).round(2)

        print(f"✅ KPI计算完成：毛利率、达成率、单位收入/成本")
        return df

    def get_summary_by_region(self) -> pd.DataFrame:
        """按区域汇总"""
        df = self.calculate_kpi()
        agg_dict = {
            "revenue": ("总收入", "sum"),
            "cost": ("总成本", "sum"),
            "gross_margin": ("平均毛利率", "mean"),
            "revenue_achievement": ("平均达成率", "mean"),
        }
        if "inventory_turnover" in df.columns:
            agg_dict["inventory_turnover"] = ("平均库存周转", "mean")
        if "delivery_ontime_rate" in df.columns:
            agg_dict["delivery_ontime_rate"] = ("平均交付及时率", "mean")

        result = df.groupby("region").agg(**{v[0]: (k, v[1]) for k, v in agg_dict.items()}).round(2)
        return result

    def get_summary_by_product(self) -> pd.DataFrame:
        """按产品线汇总"""
        df = self.calculate_kpi()
        agg_dict = {
            "revenue": ("总收入", "sum"),
            "cost": ("总成本", "sum"),
            "gross_margin": ("平均毛利率", "mean"),
            "revenue_achievement": ("平均达成率", "mean"),
        }
        if "inventory_turnover" in df.columns:
            agg_dict["inventory_turnover"] = ("平均库存周转", "mean")
        if "return_rate" in df.columns:
            agg_dict["return_rate"] = ("平均退货率", "mean")

        result = df.groupby("product_line").agg(**{v[0]: (k, v[1]) for k, v in agg_dict.items()}).round(2)
        return result

    def get_monthly_trend(self) -> pd.DataFrame:
        """月度趋势"""
        df = self.calculate_kpi()
        trend = df.groupby("month").agg(
            总收入=("revenue", "sum"),
            总成本=("cost", "sum"),
            平均毛利率=("gross_margin", "mean"),
            平均达成率=("revenue_achievement", "mean")
        ).round(2)
        return trend

    def get_full_data(self) -> pd.DataFrame:
        """获取完整KPI数据"""
        return self.calculate_kpi()
