import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
import seaborn as sns
from datetime import datetime

# 读取数据
df = pd.read_excel(
    "/Users/yangyidi/Library/CloudStorage/OneDrive-TheUniversityofHongKong-Connect/Documents/Research/Projects/Cross-border/Data/Online-shopping/HK_online.xlsx")


def generate_three_line_table(df, excel_path="Year_summary.xlsx", img_path="stats_plot.png"):
    # 生成统计量（Stata风格保留两位小数）
    try:
        print("列名列表:", df.columns.tolist())
        stats = df.groupby(df['Year'].astype(int))['HKD (million)'].agg(
            Mean=('mean'),
            Std=('std'),
            Min=('min'),
            Max=('max')
        ).reset_index().round(2)

       # 生成Excel普通表格
        stats.to_excel(excel_path, index=False, sheet_name='Year_Summary')
        print(f"Excel文件生成成功: {excel_path}")
    except Exception as e:
        print(f"Excel导出异常: {str(e)}")


generate_three_line_table(df)


def generate_latex_table_only(df, tex_path="table_only.tex"):
    stats = df.groupby(df['Year'].astype(int))['HKD (million)'].agg(
        Mean=('mean'),
        Std=('std'),
        Min=('min'),
        Max=('max')
    ).reset_index().round(2)

    latex_code = r"""\begin{table}[htbp]
\centering
\caption{Summary Statistics by Year (Billion CNY)}
\begin{tabular}{l*{4}{S[table-format=3.2]}}
\toprule
{Year} & {Mean} & {Std. Dev.} & {Min} & {Max} \\
\midrule
"""

    for _, row in stats.iterrows():
        latex_code += f"{int(row['Year'])} & {row['Mean']} & {row['Std']} & {row['Min']} & {row['Max']} \\\\\n"

    latex_code += r"""\bottomrule
\end{tabular}
\end{table}"""

    with open(tex_path, 'w') as f:
        f.write(latex_code)

    print(f"仅表格LaTeX代码生成成功: {tex_path}")


generate_latex_table_only(df)

# 年度趋势图
plt.figure(figsize=(12, 6))
annual = df.groupby('Year')['HKD (million)'].sum().reset_index()
sns.lineplot(data=annual, x='Year', y='HKD (million)',
             marker='o', linewidth=2)
# 添加以下代码强制显示整数年
plt.xticks(annual['Year'].unique())  # 仅显示数据中存在的年份
plt.title('Annual Trend of Online Retail Sales (Million HKD)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('HK_annual_trend.png', dpi=300)
plt.show()

# # 月度趋势图
# plt.figure(figsize=(14, 7))

# # 新增步骤：创建年月标签列
# df['Year-Month'] = df['Year'].astype(str) + '-' + \
#     df['Month'].astype(str).str.zfill(2)  # 格式如 2020-01
# # 或者使用更友好的文本格式
# # df['Year-Month'] = df['Month'].apply(lambda x: datetime.strptime(str(x), "%m").strftime("%b")) + ' ' + df['Year'].astype(str)

# # 修正后的绘图代码
# sns.lineplot(data=df, x='Year-Month', y='HKD (million)',
#              marker='o', linewidth=2, color='steelblue')
# # 添加以下代码强制显示整数年
# plt.xticks(annual['Year'].unique())  # 仅显示数据中存在的年份
# plt.title('Monthly Trend of Online Retail Sales (Million HKD)', fontsize=14)
# plt.xlabel('Year-Month', fontsize=12)
# plt.ylabel('Sales (Million HKD)', fontsize=12)

# # 优化刻度标签（间隔显示）
# plt.xticks(rotation=45, ha='right', fontsize=10)
# locator = plt.MaxNLocator(nbins=12)  # 强制显示所有月份
# plt.gca().xaxis.set_major_locator(locator)

# plt.grid(True, linestyle='--', alpha=0.5)
# plt.tight_layout(pad=2)  # 增加边距
