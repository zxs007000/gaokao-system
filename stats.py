import sys, sqlite3
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('data/db/gaokao.db')
c = conn.cursor()

c.execute('SELECT COUNT(*) FROM universities')
print(f'universities: {c.fetchone()[0]}')
c.execute('SELECT COUNT(*) FROM scorelines')
print(f'scorelines: {c.fetchone()[0]}')

print('\n=== 分数线来源 ===')
c.execute('SELECT source, COUNT(*) FROM scorelines GROUP BY source ORDER BY COUNT(*) DESC')
for r in c.fetchall():
    print(f'  {r[0]}: {r[1]:,}')

print('\n=== 大学详情覆盖 ===')
c.execute('SELECT COUNT(*) FROM universities WHERE ruanke_rank IS NOT NULL')
print(f'有软科排名: {c.fetchone()[0]}')
c.execute("SELECT COUNT(*) FROM universities WHERE recommend_master_rate IS NOT NULL AND recommend_master_rate != ''")
print(f'有保研率: {c.fetchone()[0]}')
c.execute('SELECT COUNT(*) FROM universities WHERE is_985 = 1')
print(f'985: {c.fetchone()[0]}')
c.execute('SELECT COUNT(*) FROM universities WHERE is_211 = 1')
print(f'211: {c.fetchone()[0]}')
c.execute('SELECT COUNT(*) FROM universities WHERE is_dual_class = 1')
print(f'双一流: {c.fetchone()[0]}')
conn.close()
