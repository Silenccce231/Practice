import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
import seaborn as sns
from datetime import datetime

# 读取数据
df = pd.read_excel(
    "/Users/yangyidi/Library/CloudStorage/OneDrive-TheUniversityofHongKong-Connect/Documents/Research/Projects/Cross-border/Data/Online-shopping/mainland_online.xlsx")


def generate_three_line_table(df, excel_path="Year_summary.xlsx", img_path="stats_plot.png"):
    # 生成统计量（Stata风格保留两位小数）
    try:
        stats = df.groupby(df['Year'].astype(int))['Absolute Value (Billion CNY)'].agg(
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
    stats = df.groupby(df['Year'].astype(int))['Absolute Value (Billion CNY)'].agg(
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
annual = df.groupby('Year')['Absolute Value (Billion CNY)'].sum().reset_index()
sns.lineplot(data=annual, x='Year', y='Absolute Value (Billion CNY)',
             marker='o', linewidth=2)
plt.title('Annual Trend of Online Retail Sales (Billion CNY)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('annual_trend.png', dpi=300)
plt.show()

# 季度趋势图
plt.figure(figsize=(12, 6))
sns.lineplot(data=df, x='Date', y='Absolute Value (Billion CNY)',
             marker='o', linewidth=2)
plt.title('Online Retail Sales Trend (Billion CNY)')
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('sales_trend_with_quarter_markers.png', dpi=300)
plt.show()
