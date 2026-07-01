import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3

db_path = r'D:\xuefeng-agent-full\ziqihe10-droid-xuefeng-agent-9badf20\admission_clean.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('=== 数据库统计 ===')
cursor.execute('SELECT COUNT(*) FROM admission')
total = cursor.fetchone()[0]
print(f'总记录数: {total}')

print('\n=== 按省份统计 ===')
cursor.execute('SELECT province, COUNT(*) as cnt FROM admission GROUP BY province ORDER BY cnt DESC')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

print('\n=== 按年份统计 ===')
cursor.execute('SELECT year, COUNT(*) as cnt FROM admission GROUP BY year ORDER BY year')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

print('\n=== 按来源统计 ===')
cursor.execute('SELECT source, COUNT(*) as cnt FROM admission GROUP BY source ORDER BY cnt DESC LIMIT 10')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

print('\n=== 示例数据（北京） ===')
cursor.execute("SELECT * FROM admission WHERE province='北京' LIMIT 5")
for row in cursor.fetchall():
    print(f'  {row}')

conn.close()
