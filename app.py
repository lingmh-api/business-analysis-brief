"""
AI驱动的企业经营分析简报自动生成系统
主应用入口 - Streamlit Web界面
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_processor import DataProcessor
from anomaly_detector import AnomalyDetector
from brief_generator import BriefGenerator
from visualizer import Visualizer

# ========== 页面配置 ==========
st.set_page_config(
    page_title="AI经营分析简报系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== 侧边栏 ==========
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=60)
    st.title("🤖 AI经营分析")
    st.caption("智能简报自动生成系统 v1.0")
    st.divider()

    st.subheader("🔑 API配置（可选）")
    api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        placeholder="sk-...（留空使用本地模式）",
        help="填入API Key可使用AI自动生成简报；留空则使用模板模式"
    )

    st.divider()
    st.subheader("📂 数据加载")
    uploaded_revenue = st.file_uploader("上传收入数据 (CSV)", type="csv", key="rev")
    uploaded_ops = st.file_uploader("上传运营数据 (CSV)", type="csv", key="ops")

    if st.button("🔄 加载示例数据", use_container_width=True):
        # 清除上传文件缓存，强制加载示例数据
        st.session_state["data_loaded"] = False
        st.session_state["data_key"] = ""
        st.session_state["use_sample"] = True
        st.rerun()

    st.divider()
    st.caption("📌 江西财经大学 · AI赋能财务以赛代训")
    st.caption("选题：AI驱动企业经营分析简报自动生成")

# ========== 标题 ==========
st.title("📊 AI驱动的企业经营分析简报自动生成系统")
st.markdown("> *AI自动检测KPI异常 → 智能归因分析 → 一键生成管理层经营简报*")

# ========== 初始化 ==========
BASE_DIR = Path(__file__).parent
if "processor" not in st.session_state:
    st.session_state["processor"] = DataProcessor(data_dir=str(BASE_DIR / "data"))
if "detector" not in st.session_state:
    st.session_state["detector"] = AnomalyDetector(threshold=0.15)
if "generator" not in st.session_state:
    st.session_state["generator"] = None
if "data_loaded" not in st.session_state:
    st.session_state["data_loaded"] = False
if "use_sample" not in st.session_state:
    st.session_state["use_sample"] = False  # 默认不加载示例数据

processor = st.session_state["processor"]
detector = st.session_state["detector"]

# ========== 数据加载逻辑（简化版） ==========
has_upload = uploaded_revenue is not None or uploaded_ops is not None

# 生成当前数据源的"指纹"，用于检测是否需要重新加载
if has_upload:
    current_key = f"upload_{uploaded_revenue.name if uploaded_revenue else 'none'}_{uploaded_ops.name if uploaded_ops else 'none'}"
else:
    current_key = "sample"

# 检查是否需要加载/重新加载
need_load = (
    not st.session_state["data_loaded"]  # 还没加载过
    or st.session_state.get("data_key", "") != current_key  # 数据源变了
    or st.session_state.get("use_sample", False) != (not has_upload)  # 模式变了
)

if need_load and (st.session_state.get("use_sample", True) or has_upload):
    with st.spinner("🔄 正在加载和处理数据..."):
        # 加载收入数据
        if uploaded_revenue is not None:
            processor.revenue_df = pd.read_csv(uploaded_revenue)
            processor.revenue_df["date"] = pd.to_datetime(processor.revenue_df["date"])
            processor.revenue_df["month"] = processor.revenue_df["date"].dt.month
            st.success(f"✅ 已上传收入数据：{len(processor.revenue_df)} 条")
        else:
            processor.load_data()  # 加载示例数据

        # 加载运营数据
        if uploaded_ops is not None:
            processor.operations_df = pd.read_csv(uploaded_ops)
            processor.operations_df["date"] = pd.to_datetime(processor.operations_df["date"])
            processor.operations_df["month"] = processor.operations_df["date"].dt.month
            st.success(f"✅ 已上传运营数据：{len(processor.operations_df)} 条")

        # 清理和计算
        processor.clean_data()
        df = processor.calculate_kpi()

        # 异常检测
        anomaly_df = detector.detect_all(df)

        # 存储到session
        st.session_state["df"] = df
        st.session_state["anomaly_df"] = anomaly_df
        st.session_state["data_loaded"] = True
        st.session_state["data_key"] = current_key
        st.session_state["use_sample"] = not has_upload

        # 初始化AI生成器
        if api_key:
            st.session_state["generator"] = BriefGenerator(api_key=api_key)
        else:
            st.session_state["generator"] = BriefGenerator(api_key="")

        st.success("🎉 数据加载完成！")

# ========== 主界面 Tabs ==========
if st.session_state["data_loaded"]:
    df = st.session_state["df"]
    anomaly_df = st.session_state["anomaly_df"]
    generator = st.session_state["generator"]

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📈 KPI看板", "🔍 异常检测", "💬 NL2SQL问数", "📝 简报生成"]
    )

    # ===== Tab 1: KPI看板 =====
    with tab1:
        st.subheader("📈 核心KPI看板")

        # KPI指标卡
        col1, col2, col3, col4 = st.columns(4)
        total_revenue = df["revenue"].sum()
        total_cost = df["cost"].sum()
        avg_margin = ((total_revenue - total_cost) / total_revenue * 100)
        avg_achievement = (df["revenue"].sum() / df["revenue_target"].sum() * 100)

        with col1:
            st.metric("💰 累计总收入", f"¥{total_revenue/10000:.1f}万")
        with col2:
            st.metric("📊 平均毛利率", f"{avg_margin:.1f}%")
        with col3:
            st.metric("🎯 收入达成率", f"{avg_achievement:.1f}%",
                      delta=f"{avg_achievement - 100:.1f}%")
        with col4:
            st.metric("⚠️ 异常数量", f"{len(anomaly_df)}个",
                      delta_color="inverse")

        st.divider()

        # 图表行
        col_left, col_right = st.columns(2)
        with col_left:
            st.plotly_chart(
                Visualizer.revenue_by_region(df),
                use_container_width=True
            )
        with col_right:
            st.plotly_chart(
                Visualizer.margin_by_product(df),
                use_container_width=True
            )

        st.plotly_chart(
            Visualizer.monthly_trend(df),
            use_container_width=True
        )

        # 数据表格
        with st.expander("📋 查看原始数据"):
            st.dataframe(df, use_container_width=True)

    # ===== Tab 2: 异常检测 =====
    with tab2:
        st.subheader("🔍 KPI异常检测结果")

        if anomaly_df.empty:
            st.success("✅ 未检测到KPI异常，所有指标运行平稳！")
        else:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.dataframe(anomaly_df, use_container_width=True,
                             hide_index=True)
            with col2:
                # 异常分类统计
                type_counts = anomaly_df["类型"].value_counts()
                st.markdown("### 异常分类统计")
                for t, c in type_counts.items():
                    st.metric(t, f"{c} 项")

                severe_count = len(anomaly_df[anomaly_df["严重程度"].str.contains("严重")])
                st.metric("🚨 严重异常", f"{severe_count} 项")

            st.divider()
            st.plotly_chart(
                Visualizer.anomaly_heatmap(anomaly_df, df),
                use_container_width=True
            )

            # 异常摘要
            st.markdown("### 📋 AI异常摘要")
            st.markdown(detector.get_anomaly_summary())

    # ===== Tab 3: NL2SQL问数 =====
    with tab3:
        st.subheader("💬 自然语言问数（NL2SQL）")
        st.caption("用自然语言向数据提问，AI自动转换为SQL查询并返回结果")

        # 预设问题
        preset_questions = [
            "华南区产品A上个月的毛利率是多少？",
            "哪个区域的收入达成率最低？",
            "库存周转率低于3.5的产品线有哪些？",
            "6月份收入最高的区域和产品线是什么？",
            "哪些月份的毛利率低于35%？"
        ]

        col_presets, col_custom = st.columns([1, 2])
        with col_presets:
            st.markdown("**快捷提问**")
            for q in preset_questions:
                if st.button(q, key=f"q_{q[:10]}", use_container_width=True):
                    st.session_state["nl_question"] = q

        with col_custom:
            question = st.text_area(
                "🔍 输入你的问题",
                value=st.session_state.get("nl_question", ""),
                placeholder="例如：华东区产品B近3个月的收入趋势如何？",
                height=100
            )
            if st.button("🚀 AI分析", type="primary", use_container_width=True):
                if question and generator:
                    with st.spinner("🤔 AI正在分析您的问题..."):
                        table_schema = """
                        表名: business_data
                        字段: date(日期), region(区域), product_line(产品线),
                              channel(渠道), revenue(收入), revenue_target(目标收入),
                              cost(成本), quantity(数量), gross_margin(毛利率),
                              revenue_achievement(达成率), inventory_turnover(库存周转),
                              accounts_receivable_days(应收账款天数),
                              delivery_ontime_rate(交付及时率), return_rate(退货率)
                        """
                        sample = df.head(3).to_string()
                        response = generator.generate_nl2sql_response(
                            question, table_schema, sample
                        )
                        st.markdown(response)

    # ===== Tab 4: 简报生成 =====
    with tab4:
        st.subheader("📝 经营分析简报自动生成")

        if st.button("🤖 一键生成经营分析简报", type="primary",
                     use_container_width=True, disabled=not generator):
            with st.spinner("🤖 AI正在生成经营分析简报..."):

                # 准备简报数据
                region_summary_df = processor.get_summary_by_region()
                product_summary_df = processor.get_summary_by_product()
                trend_df = processor.get_monthly_trend()
                anomaly_summary = detector.get_anomaly_summary()

                # KPI摘要
                kpi_text = f"""
| 指标 | 数值 |
|------|------|
| 累计总收入 | ¥{total_revenue:,.0f} |
| 累计总成本 | ¥{total_cost:,.0f} |
| 平均毛利率 | {avg_margin:.1f}% |
| 收入达成率 | {avg_achievement:.1f}% |
| 检测异常数 | {len(anomaly_df)} 项 |
"""

                # 趋势描述
                trend_lines = []
                for _, row in trend_df.iterrows():
                    trend_lines.append(
                        f"- {int(row.name)}月：收入¥{row['总收入']:,.0f}，"
                        f"毛利率{row['平均毛利率']:.1f}%，达成率{row['平均达成率']:.1f}%"
                    )
                trend_desc = "\n".join(trend_lines)

                # 生成简报
                brief = generator.generate_brief(
                    kpi_summary=kpi_text,
                    anomaly_summary=anomaly_summary,
                    region_summary=region_summary_df.to_markdown(),
                    product_summary=product_summary_df.to_markdown(),
                    trend_desc=trend_desc
                )

                st.session_state["brief_content"] = brief

        # 显示简报
        if "brief_content" in st.session_state:
            st.divider()
            st.markdown(st.session_state["brief_content"])

            # 导出按钮
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button(
                    "📥 下载简报 (Markdown)",
                    st.session_state["brief_content"],
                    file_name="经营分析简报.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            with col_dl2:
                # 复制按钮模拟
                st.button("📋 复制简报内容", use_container_width=True,
                          help="请手动全选复制")

else:
    # 未加载数据时的欢迎页
    st.info("👈 请先在左侧上传数据文件，或点击「加载示例数据」开始体验")
    st.markdown("""
    ### 🚀 快速开始

    1. **加载数据**：上传CSV格式的经营数据（收入+运营），或使用示例数据
    2. **KPI看板**：自动计算毛利率、达成率等核心指标并可视化
    3. **异常检测**：AI自动扫描多维度KPI异常并生成预警
    4. **NL2SQL问数**：用自然语言提问，AI自动转SQL并解读
    5. **简报生成**：一键生成结构化经营分析简报

    ### 📊 数据格式要求

    收入数据CSV需包含：`date, region, product_line, channel, revenue, revenue_target, cost, quantity`

    运营数据CSV需包含：`date, region, product_line, inventory_turnover, accounts_receivable_days, delivery_ontime_rate, return_rate`
    """)

# ========== 底部 ==========
st.divider()
st.caption("🤖 AI驱动企业经营分析简报自动生成系统 | 江西财经大学 | 2026")
