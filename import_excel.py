import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
from crawler.database import Database
from crawler.models import EnrollmentPlanDetail

def import_excel(file_path: str):
    """导入Excel招生计划数据"""
    print(f'读取文件: {file_path}')
    xl = pd.ExcelFile(file_path)
    print(f'Sheet列表: {xl.sheet_names}')

    db = Database('data/db/gaokao.db')
    total_imported = 0

    for sheet_name in xl.sheet_names:
        if sheet_name in ['作者信息，请勿删除']:
            continue

        print(f'\n处理Sheet: {sheet_name}')
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        if df.empty:
            print(f'  空Sheet，跳过')
            continue

        print(f'  行数: {len(df)}, 列数: {len(df.columns)}')

        plans = []
        for _, row in df.iterrows():
            try:
                plan = EnrollmentPlanDetail(
                    batch=str(row.get('批次', '')),
                    enrollment_type=str(row.get('招生类型', '')),
                    university_name=str(row.get('院校名称', '')),
                    major_group_code=str(row.get('专业组代码', '')),
                    major_group_name=str(row.get('专业组名称', '')),
                    major_code=str(row.get('专业代码', '')),
                    major_name=str(row.get('专业名称', '')),
                    subject_requirement=str(row.get('科目要求', '')),
                    notes=str(row.get('备注', '')),
                    duration=str(row.get('学制', '')),
                    tuition=str(row.get('收费标准', '')),
                    school_nature=str(row.get('办学性质', '')),
                    university_level=str(row.get('院校层次', '')),
                    first_class_type=str(row.get('一流类型', '')),
                    direct_department=str(row.get('直属部门', '')),
                    province=str(row.get('省份', '')),
                    city=str(row.get('城市', '')),
                    city_nature=str(row.get('城市性质', '')),
                    plan_2025=int(row['2025年招生计划']) if pd.notna(row.get('2025年招生计划')) else None,
                    score_2024=int(row['2024最低分']) if pd.notna(row.get('2024最低分')) else None,
                    rank_2024=int(row['2024位次']) if pd.notna(row.get('2024位次')) else None,
                    score_2023=int(row['2023最低分']) if pd.notna(row.get('2023最低分')) else None,
                    rank_2023=int(row['2023位次']) if pd.notna(row.get('2023位次')) else None,
                    score_2022=int(row['2022最低分']) if pd.notna(row.get('2022最低分')) else None,
                    rank_2022=int(row['2022位次']) if pd.notna(row.get('2022位次')) else None,
                    discipline_evaluation=str(row.get('学科评估', '')),
                    postgrad_recommend_rate=str(row.get('保研率', '')),
                    first_level_discipline=str(row.get('一级学科', '')),
                    second_level_category=str(row.get('二级大类', '')),
                    ranking_shanghai=str(row.get('软科2023年排名', '')),
                    ranking_summary=str(row.get('排名汇总', '')),
                    doctoral_programs=str(row.get('博士点数', '')),
                    master_programs=str(row.get('硕士点数', '')),
                    school_type=str(row.get('学校性质', '')),
                    source='excel'
                )
                plans.append(plan)
            except Exception as e:
                print(f'  跳过行: {e}')

        if plans:
            count = db.insert_enrollment_plans_batch(plans)
            print(f'  导入 {count} 条')
            total_imported += count

    print(f'\n=== 导入完成 ===')
    print(f'总计导入: {total_imported} 条招生计划')

if __name__ == '__main__':
    file_path = r'D:\MyVault\内容\天津2025招生计划及录取分数_高报师版new.xlsx'
    import_excel(file_path)
