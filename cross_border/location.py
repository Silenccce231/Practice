import pandas as pd

# ========== 修改以下路径为你的实际文件路径 ========== #
# 文件1的绝对路径（需要匹配经纬度的主文件）
file1_path = "/Users/yangyidi/Library/CloudStorage/OneDrive-TheUniversityofHongKong-Connect/Documents/Research/Projects/Cross-border/Data/EPRC_v3.xlsx"

# 文件2的绝对路径（包含STREET、latitude、longitude的数据源）
file2_path = "/Users/yangyidi/Library/CloudStorage/OneDrive-TheUniversityofHongKong-Connect/Documents/Research/Projects/Cross-border/Basic_material/EPRC_raw.xlsx"

# 输出文件的保存路径（按需修改）
output_path = "/Users/yangyidi/Library/CloudStorage/OneDrive-TheUniversityofHongKong-Connect/Documents/Research/Projects/Cross-border/Data/EPRC_v3.1.xlsx"
# ============================================== #

try:
    # 读取文件
    df1 = pd.read_excel(file1_path)
    df2 = pd.read_excel(file2_path)

    print(df1.columns)
    print(df2.columns)

    # ----- 关键修改：对文件2按STREET去重，保留第一个出现的经纬度 -----
    df2 = df2.drop_duplicates(subset="STREET", keep="first")

    # 合并数据
    merged_df = pd.merge(
        df1,
        df2[["STREET", "LATITUDE", "LONGTITUDE"]],
        on="STREET",
        how="left"
    )

    # 保存结果到指定路径
    merged_df.to_excel(output_path, index=False)
    print(f"合并完成！文件已保存至：{output_path}")

    # 验证行数是否与文件1一致
    print(f"文件1行数：{len(df1)}，合并后行数：{len(merged_df)}")

except FileNotFoundError as e:
    print("错误：文件未找到，请检查路径是否正确 ->", e)
except KeyError as e:
    print("错误：列名不存在，请检查Excel文件中是否包含'STREET', 'LATITUDE', 'LONGTITUDE'列 ->", e)
except Exception as e:
    print("未知错误：", e)
