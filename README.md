# 📊 AI驱动的企业经营分析简报自动生成系统

> **选题**：经营分析赛道 | AI赋能财务·以赛代训
>
> 江西财经大学 · 信息与数学学院 · 2026年7月

---

## 🎯 项目概述

本系统利用AI技术（大语言模型 + 数据分析），实现企业经营数据的**自动异常检测**、**自然语言问数（NL2SQL）** 和**管理层经营简报一键生成**。

解决企业传统经营分析中"数据整合慢→异常发现漏→简报撰写累"的链式痛点。

---

## 🚀 快速启动

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置API Key（可选）
```bash
# 创建 .env 文件
echo DEEPSEEK_API_KEY=your_key_here > .env
```
> 不配置API Key也可运行，系统将使用本地模板模式生成简报。

### 3. 启动应用
```bash
streamlit run app.py
```

### 4. 运行测试
```bash
python test_all.py
```

---

## 📁 项目结构

```
business-analysis-brief/
├── app.py                  # Streamlit 主应用入口
├── test_all.py             # 全模块测试脚本
├── requirements.txt        # Python 依赖
├── src/
│   ├── __init__.py
│   ├── data_processor.py   # 数据处理与KPI计算
│   ├── anomaly_detector.py # 多维度KPI异常检测
│   ├── brief_generator.py  # AI简报生成 + NL2SQL
│   └── visualizer.py       # Plotly可视化引擎
├── data/
│   ├── revenue_data.csv    # 模拟收入数据（6个月×3区域×2产品线）
│   └── operations_data.csv # 模拟运营数据
├── docs/
│   ├── 01-立项简报.md       # Day1：一页立项简报
│   ├── 02-方案设计.md       # Day2：方案设计文档
│   ├── 03-PPT内容大纲.md    # Day4：PPT内容大纲
│   ├── 04-答辩准备.md       # Day4：答辩三问详细准备
│   └── 05-提示词文档.md     # 鼓励提交：AI提示词文档
└── output/                 # 简报输出目录
```

---

## 🧠 核心技术

| 模块 | 技术 | 说明 |
|------|------|------|
| 数据处理 | Pandas + NumPy | 数据清洗、KPI计算、多维度汇总 |
| 异常检测 | 规则引擎 + IQR | 6大异常检测规则，多维度交叉扫描 |
| NL2SQL | DeepSeek API | 自然语言→SQL→执行→结果解读 |
| 简报生成 | DeepSeek API | 数据→结构化Markdown简报 |
| 可视化 | Plotly | 交互式图表（柱状图、趋势图、雷达图、热力图） |
| 前端 | Streamlit | 轻量级Web交互界面 |

---

## 📊 示例数据说明

系统内置6个月的模拟企业经营数据：

- **3个区域**：华北、华东、华南
- **2条产品线**：产品A、产品B
- **2个渠道**：线上、线下
- **36条记录**，涵盖收入、成本、运营KPI

---

## 🏆 答辩三问

| 问题 | 回答要点 |
|------|----------|
| ① 解决什么问题？ | 经营分析中数据整合慢→异常发现漏→简报撰写累 |
| ② AI的角色？ | 核心引擎：异常检测、NL2SQL、简报生成 |
| ③ 业务价值？ | 简报生产3-5天→分钟级，异常发现准确率↑25% |

---

## 📝 许可证

本项目为学术实训作品，江西财经大学2026。
