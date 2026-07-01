import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3

db_path = r'D:\xuefeng-agent-full\ziqihe10-droid-xuefeng-agent-9badf20\admission_clean.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 获取所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables:', [t[0] for t in tables])

# 查看每个表的结构和数据量
for table_name in [t[0] for t in tables]:
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    count = cursor.fetchone()[0]

    cursor.execute(f'PRAGMA table_info({table_name})')
    columns = cursor.fetchall()
    col_names = [col[1] for col in columns]

    print(f'\n{table_name}: {count} rows')
    print(f'  Columns: {col_names}')

    # 显示前3行
    cursor.execute(f'SELECT * FROM {table_name} LIMIT 3')
    rows = cursor.fetchall()
    for row in rows:
        print(f'  {row}')

conn.close()
