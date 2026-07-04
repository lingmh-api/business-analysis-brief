"""
简报生成模块：调用大模型API自动生成经营分析简报
"""
import os
from typing import Optional


class BriefGenerator:
    """AI简报生成器"""

    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-chat"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.model = model
        self.client = None
        self._init_client()

    def _init_client(self):
        """初始化大模型客户端"""
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.deepseek.com"
                )
                print("✅ DeepSeek API 客户端初始化成功")
            except Exception as e:
                print(f"⚠️ API客户端初始化失败：{e}")
                print("💡 将使用本地模板模式生成简报")
        else:
            print("💡 未配置API Key，将使用本地模板模式生成简报")

    def generate_brief(
        self,
        kpi_summary: str,
        anomaly_summary: str,
        region_summary: str,
        product_summary: str,
        trend_desc: str
    ) -> str:
        """调用AI生成经营分析简报"""
        prompt = f"""你是一位资深企业财务分析师。请根据以下经营数据，生成一份专业的月度经营分析简报。

## 数据输入

### KPI总览
{kpi_summary}

### 异常检测
{anomaly_summary}

### 区域分析
{region_summary}

### 产品线分析
{product_summary}

### 趋势分析
{trend_desc}

## 输出要求
请按以下结构生成简报（使用Markdown格式）：

1. **经营概览**（2-3句话总结本月整体经营状况）
2. **核心KPI看板**（关键指标一览，使用表格）
3. **异常预警与归因**（重点分析异常指标的可能原因）
4. **区域/产品线亮点与风险**（对比各区域、各产品线表现）
5. **趋势判断**（基于月度趋势给出前瞻性判断）
6. **行动建议**（3-5条可落地的改善建议）

要求：语言专业但易懂，数据引用准确，分析有深度，建议可落地。"""

        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一位资深企业财务分析师，擅长经营分析简报撰写。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=3000
                )
                content = response.choices[0].message.content
                print("✅ AI简报生成成功")
                return content
            except Exception as e:
                print(f"❌ AI生成失败：{e}")
                print("💡 回退到本地模板模式")

        return self._generate_template_brief(
            kpi_summary, anomaly_summary, region_summary, product_summary, trend_desc
        )

    def _generate_template_brief(
        self,
        kpi_summary: str,
        anomaly_summary: str,
        region_summary: str,
        product_summary: str,
        trend_desc: str
    ) -> str:
        """本地模板模式生成简报（不依赖API）"""
        return f"""# 📊 企业月度经营分析简报

---

## 一、经营概览

本月企业经营整体运行平稳，部分区域与产品线出现结构性波动，需重点关注华北区域的收入达成与库存周转改善。AI自动检测发现若干异常信号，建议管理层重点关注。

---

## 二、核心KPI看板

{kpi_summary}

---

## 三、异常预警与归因分析

{anomaly_summary}

> 💡 **AI归因提示**：异常主要集中在华北区域收入达成率偏低及部分月份毛利率波动。建议结合市场环境、促销活动、原材料价格等外部因素深入归因。

---

## 四、区域与产品线分析

### 区域表现
{region_summary}

### 产品线表现
{product_summary}

---

## 五、趋势判断

{trend_desc}

- 📈 **积极信号**：华东区域持续增长，产品A表现稳定
- 📉 **关注信号**：华北区域收入波动较大，需关注Q3表现
- 🔄 **中性观察**：华南区域波动在正常范围内

---

## 六、行动建议

1. **华北区域专项复盘**：针对华北区域产品B收入达成率偏低问题，建议开展区域经营复盘会
2. **库存优化**：华北区域库存周转率持续偏低，建议优化库存策略，减少滞销品占比
3. **应收账款管控**：针对应收账款天数偏高的区域，加强催收力度，优化信用政策
4. **毛利率监控**：建立毛利率月度预警机制，对波动超过5pp的产品线自动触发分析
5. **AI持续跟踪**：建议将本系统接入月度经营分析流程，实现异常自动预警与简报自动生成

---

*📅 报告生成时间：自动生成 | 🤖 生成引擎：AI智能分析系统 v1.0*
"""

    def generate_nl2sql_response(self, question: str, table_schema: str, sample_data: str) -> str:
        """NL2SQL：自然语言转SQL查询"""
        if not self.client:
            return self._simulate_nl2sql(question)

        prompt = f"""你是一个SQL专家。根据以下数据表结构，将用户的自然语言问题转换为SQL查询。

## 表结构
{table_schema}

## 示例数据
{sample_data}

## 用户问题
{question}

请返回：
1. SQL查询语句
2. 查询结果的业务解读（用中文简要说明）"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是SQL专家，擅长将自然语言转为SQL查询并解读结果。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ NL2SQL生成失败：{e}")
            return self._simulate_nl2sql(question)

    def _simulate_nl2sql(self, question: str) -> str:
        """模拟NL2SQL响应（演示用）"""
        return f"""## SQL查询
```sql
SELECT region, product_line, SUM(revenue) as total_revenue, 
       AVG(gross_margin) as avg_margin
FROM business_data
WHERE month = 6
GROUP BY region, product_line
ORDER BY total_revenue DESC;
```

## 业务解读
针对您的问题「{question}」：

本月各区域产品线表现如下：
- 华东区域仍是收入主力，产品A和产品B均表现优异
- 华北区域收入相对疲软，需重点关注
- 建议结合毛利率与收入规模综合评估各产品线健康度
"""
