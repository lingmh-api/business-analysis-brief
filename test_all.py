"""测试脚本：验证所有模块功能"""
import sys
sys.path.insert(0, 'src')

from data_processor import DataProcessor
from anomaly_detector import AnomalyDetector
from brief_generator import BriefGenerator
from visualizer import Visualizer

# 准备数据
dp = DataProcessor(data_dir='data')
dp.load_data()
dp.clean_data()
df = dp.calculate_kpi()

detector = AnomalyDetector(threshold=0.15)
anomaly_df = detector.detect_all(df)

# 测试模板简报
print('=== 测试简报生成（模板模式） ===')
gen = BriefGenerator(api_key='')
region_summary = dp.get_summary_by_region().to_markdown()
product_summary = dp.get_summary_by_product().to_markdown()
trend_df = dp.get_monthly_trend()

trend_lines = []
for idx, row in trend_df.iterrows():
    rev = row['总收入']
    margin = row['平均毛利率']
    trend_lines.append(f'- {int(idx)}月：收入{rev:,.0f}，毛利率{margin:.1f}%')
trend_desc = '\n'.join(trend_lines)

brief = gen.generate_brief(
    kpi_summary='| 指标 | 数值 |\n|------|------|\n| 累计收入 | 55,660,000 |\n| 平均毛利率 | 39.2% |',
    anomaly_summary=detector.get_anomaly_summary(),
    region_summary=region_summary,
    product_summary=product_summary,
    trend_desc=trend_desc
)
print(brief[:600])
print('\n...(简报生成成功)')

# 测试可视化
print('\n=== 测试可视化模块 ===')
fig1 = Visualizer.revenue_by_region(df)
print(f'✅ 区域收入图: {type(fig1).__name__}')
fig2 = Visualizer.monthly_trend(df)
print(f'✅ 月度趋势图: {type(fig2).__name__}')
fig3 = Visualizer.operations_radar(df)
print(f'✅ 运营雷达图: {type(fig3).__name__}')
fig4 = Visualizer.margin_by_product(df)
print(f'✅ 产品毛利率图: {type(fig4).__name__}')
fig5 = Visualizer.achievement_gauge(df)
print(f'✅ 达成率仪表盘: {type(fig5).__name__}')

print('\n🎉 所有模块测试通过！')
