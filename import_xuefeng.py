import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
from crawler.database import Database
from crawler.models import ScoreLine

def import_xuefeng_data():
    """从xuefeng数据库导入录取数据"""
    src_path = r'D:\xuefeng-agent-full\ziqihe10-droid-xuefeng-agent-9badf20\admission_clean.db'
    dst_path = 'data/db/gaokao.db'

    print(f'读取源数据库: {src_path}')
    src_conn = sqlite3.connect(src_path)
    src_cursor = src_conn.cursor()

    print(f'连接目标数据库: {dst_path}')
    db = Database(dst_path)

    # 获取总数
    src_cursor.execute('SELECT COUNT(*) FROM admission')
    total = src_cursor.fetchone()[0]
    print(f'源数据库共有 {total} 条记录')

    # 分批导入
    batch_size = 10000
    imported = 0
    skipped = 0

    src_cursor.execute('SELECT province, year, school, major, score, rank FROM admission')
    
    batch = []
    while True:
        row = src_cursor.fetchone()
        if not row:
            break

        province, year, school, major, score, rank = row

        # 跳过无效数据
        if not school or not score:
            skipped += 1
            continue

        try:
            score_int = int(score) if score else None
            rank_int = int(rank) if rank else None
            year_int = int(year) if year else None

            if not year_int or not score_int:
                skipped += 1
                continue

            line = ScoreLine(
                university_name=school,
                province=province,
                year=year_int,
                batch='',
                min_score=score_int,
                min_rank=rank_int,
                major_name=major,
                source='xuefeng'
            )
            batch.append(line)

            if len(batch) >= batch_size:
                for b in batch:
                    db.insert_scoreline(b)
                imported += len(batch)
                print(f'  已导入: {imported}/{total} (跳过: {skipped})')
                batch = []

        except Exception as e:
            skipped += 1

    # 导入剩余数据
    if batch:
        for b in batch:
            db.insert_scoreline(b)
        imported += len(batch)

    src_conn.close()
    print(f'\n=== 导入完成 ===')
    print(f'导入: {imported} 条')
    print(f'跳过: {skipped} 条')

if __name__ == '__main__':
    import_xuefeng_data()
