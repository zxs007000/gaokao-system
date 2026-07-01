"""
Import 2025 provincial 投档线 (admission score lines) from Baidu Netdisk downloads.
Handles 30+ provinces each with unique XLSX/XLS column structures.
Target: scorelines table in gaokao.db
"""
import pandas as pd
import sqlite3
import os
import re
import sys

BASE = "D:/BaiduNetdiskDownload"
DB_PATH = "D:/gaokao-system/data/db/gaokao.db"

# Province name guessing from filename
def guess_province(fname):
    provinces = [
        '北京','天津','上海','重庆','河北','山西','辽宁','吉林','黑龙江',
        '江苏','浙江','安徽','福建','江西','山东','河南','湖北','湖南',
        '广东','广西','海南','四川','贵州','云南','陕西','甘肃','青海',
        '宁夏','新疆','内蒙古','西藏',
    ]
    for p in provinces:
        if p in fname:
            return p
    return None

def safe_int(val):
    """Convert to int, return None if not possible"""
    if pd.isna(val):
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None

def safe_str(val):
    if pd.isna(val):
        return None
    return str(val).strip()

def find_univ_col(df):
    """Find the column most likely containing university names"""
    for col in df.columns:
        col_str = str(col)
        if any(kw in col_str for kw in ['院校名称', '大学名称', '高校名称', '院校专业组名称',
                                          '院校代号及名称', '院校、专业组', '学校名称']):
            return col
    # Heuristic: look for column with values ending in 大学/学院/学校
    for col in df.columns:
        if df[col].dtype == object:
            sample = df[col].dropna().head(20).astype(str)
            if sample.str.contains('大学|学院|学校').sum() > 5:
                return col
    return None

def find_score_col(df):
    for col in df.columns:
        col_str = str(col)
        if any(kw in col_str for kw in ['投档分', '最低分', '投档最低分', '投档线', '分数线', '录取分', '分数段']):
            return col
    # Heuristic: look for column with numeric values in 300-750 range
    for col in df.columns:
        if df[col].dtype in ('int64', 'float64'):
            vals = df[col].dropna()
            if len(vals) > 10:
                if 300 < vals.median() < 900:
                    return col
    return None

def find_rank_col(df):
    for col in df.columns:
        col_str = str(col)
        if any(kw in col_str for kw in ['位次', '排位', '排名', '投档最低排位', '最低位次']):
            return col
    return None

def find_batch_col(df):
    for col in df.columns:
        col_str = str(col)
        if '批次' in col_str:
            return col
    return None

def find_subject_col(df):
    for col in df.columns:
        col_str = str(col)
        if any(kw in col_str for kw in ['科类', '选科', '首选', '科目']):
            return col
    return None

def find_major_col(df):
    for col in df.columns:
        col_str = str(col)
        if any(kw in col_str for kw in ['专业组名称', '专业名称', '专业组', '专业']):
            return col
    return None

def find_year_col(df):
    for col in df.columns:
        col_str = str(col)
        if col_str == '年份':
            return col
    return None

# ============================================================
# Parse individual file
# ============================================================
def parse_scoreline_file(filepath, fname):
    """Parse a scoreline XLSX and return list of (province, year, batch, subject, univ, major, score, rank) tuples"""
    province = guess_province(fname)
    year = 2025  # All these files are 2025
    
    results = []
    
    try:
        if filepath.endswith('.xls'):
            # Try xlrd first, fall back to openpyxl
            try:
                df = pd.read_excel(filepath, header=None, engine='xlrd')
            except Exception:
                df = pd.read_excel(filepath, header=None, engine='openpyxl')
        else:
            df = pd.read_excel(filepath, header=None)
    except Exception as e:
        # Last resort: try the opposite engine
        try:
            if filepath.endswith('.xls'):
                df = pd.read_excel(filepath, header=None, engine='openpyxl')
            else:
                df = pd.read_excel(filepath, header=None, engine='xlrd')
        except Exception as e2:
            print(f"  SKIP {fname}: read error: {e2}")
            return results
    
    if df.empty:
        return results
    
    # --- Find header row ---
    # Header row is the one that contains key column names
    univ_keywords = ['院校名称', '院校代号', '大学名称', '院校代码', 
                     '院校专业组名称', '院校专业组代号', '院校、专业组',
                     '院校代号及名称', '院校专业组名称', '院校名称',
                     '学校名称', '校名']
    score_keywords = ['投档', '分数', '最低分', '投档分', '投档线', '投档最低分', '投档最低分']
    
    header_row = None
    for i in range(min(12, len(df))):
        # Use replace('\n', '') not strip() so that '院校专业\n组名称' → '院校专业组名称'
        row_vals = [str(v).replace('\n', '').strip() for v in df.iloc[i].dropna().values]
        row_text = ' '.join(row_vals)
        if any(kw in row_text for kw in univ_keywords):
            if any(kw in row_text for kw in score_keywords):
                header_row = i
                break

    if header_row is None:
        # Try again with broader match
        for i in range(min(12, len(df))):
            row_vals = [str(v).replace('\n', '').strip() for v in df.iloc[i].dropna().values]
            row_text = ' '.join(row_vals)
            if any(kw in row_text for kw in univ_keywords):
                header_row = i
                break
    
    if header_row is None:
        print(f"  SKIP {fname}: can't find header row (univ={univ_keywords[:4]}...)")
        return results
    
    # For files with sub-header rows (like Shanghai row2=header, row3=sub-headers),
    # skip sub-header rows by checking if the next row is data
    # A data row has numeric values or looks like a school name
    data_start = header_row + 1
    for check_row in range(header_row + 1, min(header_row + 4, len(df))):
        vals = [str(v).strip() for v in df.iloc[check_row].dropna().values[:3]]
        val_text = ' '.join(vals)
        # If this row re-contains header keywords like '院校' or '投档', it's likely a sub-header
        if any(kw in val_text for kw in ['院校名称', '院校代号', '投档', '最低分', '分数']):
            continue  # skip sub-header
        # Otherwise it's likely data or empty
        if len(vals) > 0:
            data_start = check_row
            break
    
    # Set header and extract data
    headers = [str(v).strip().replace('\n', '') for v in df.iloc[header_row].values]
    data = df.iloc[data_start:].copy()
    data.columns = headers
    
    # Skip rows that are sub-headers or empty
    data = data.dropna(subset=[c for c in data.columns if c != 'nan' and 'nan' not in c], how='all')
    
    # Find key columns
    univ_col = find_univ_col(data)
    score_col = find_score_col(data)
    rank_col = find_rank_col(data)
    batch_col = find_batch_col(data)
    subject_col = find_subject_col(data)
    major_col = find_major_col(data)
    year_col = find_year_col(data)
    
    if univ_col is None:
        print(f"  SKIP {fname}: can't find university column. Headers: {headers[:8]}")
        return results
    
    if score_col is None:
        print(f"  SKIP {fname}: can't find score column. Headers: {headers[:8]}")
        return results
    
    # Determine year
    if year_col and year_col in data.columns:
        years = data[year_col].dropna()
        if len(years) > 0:
            year = safe_int(years.iloc[0]) or 2025
    
    # Extract records
    for _, row in data.iterrows():
        univ = safe_str(row.get(univ_col))
        if univ is None:
            continue
        
        # Clean university name:
        # "A001北京大学" → "北京大学" (Shandong format)
        # "北京大学(01)" → "北京大学" (Shanghai/Hainan format)  
        cleaned_univ = univ
        m = re.match(r'[A-Z]?\d+\s*(.+)', cleaned_univ)
        if m:
            cleaned_univ = m.group(1).strip()
        cleaned_univ = re.sub(r'\([^)]*\)$', '', cleaned_univ).strip()
        
        # If univ_col is "院校专业组名称" or "院校、专业组", also extract major info
        major_from_univ = None
        if '专业组' in str(univ_col) and not major_col:
            # Try to extract from combined field like "北京大学(01)" or "北京大学第01组"
            m = re.search(r'[\(（]([^)）]*)[\)）]', univ)
            if m:
                major_from_univ = m.group(1)
            else:
                m = re.search(r'(第\S*组)', univ)
                if m:
                    major_from_univ = m.group(1)
        
        score = safe_int(row.get(score_col))
        if score is None:
            continue
        rank_val = safe_int(row.get(rank_col)) if rank_col and rank_col in data.columns else None
        batch = safe_str(row.get(batch_col)) if batch_col and batch_col in data.columns else '本科批'
        subject = safe_str(row.get(subject_col)) if subject_col and subject_col in data.columns else None
        major = safe_str(row.get(major_col)) if major_col and major_col in data.columns else major_from_univ
        
        results.append((province, year, batch, subject, cleaned_univ, major, score, rank_val))
    
    return results

# ============================================================
# Parse Henan enrollment plan
# ============================================================
def parse_enrollment_file(filepath):
    """Parse Henan 2025 enrollment plan and return list of dicts"""
    results = []
    try:
        df = pd.read_excel(filepath, nrows=0)
        if '生源地' not in str(df.columns):
            df = pd.read_excel(filepath, header=None)
            headers = [str(v).strip() for v in df.iloc[0].values]
            data = df.iloc[1:].copy()
            data.columns = headers
        else:
            data = df
        
        for _, row in data.iterrows():
            province = safe_str(row.get('生源地'))
            year = safe_int(row.get('年份'))
            batch = safe_str(row.get('批次'))
            subject = safe_str(row.get('科类'))
            univ = safe_str(row.get('院校名称'))
            major_group = safe_str(row.get('专业组代码'))
            major_code = safe_str(row.get('专业代码'))
            major_name = safe_str(row.get('专业名称'))
            major_notes = safe_str(row.get('专业备注'))
            subject_req = safe_str(row.get('选科要求'))
            duration = safe_str(row.get('学制'))
            tuition = safe_str(row.get('学费'))
            quota = safe_int(row.get('计划人数'))
            
            if univ is None:
                continue
            
            results.append({
                'province': province or '河南',
                'year': year or 2025,
                'batch': batch,
                'subject': subject,
                'university_name': univ,
                'major_group_code': str(major_group) if major_group else None,
                'major_code': str(major_code) if major_code else None,
                'major_name': major_name,
                'subject_requirement': subject_req,
                'notes': major_notes,
                'duration': str(duration) if duration else None,
                'tuition': str(tuition) if tuition else None,
                'quota': quota,
            })
    except Exception as e:
        print(f"  SKIP enrollment: {e}")
    return results

# ============================================================
# Parse Henan professional score data (richer)
# ============================================================
def parse_henan_professional_scores(filepath):
    """Parse 25年全国高校在河南的专业录取分数.xlsx → scorelines with more metadata"""
    results = []
    try:
        df = pd.read_excel(filepath)
        for _, row in df.iterrows():
            year = safe_int(row.get('年份'))
            univ = safe_str(row.get('院校名称'))
            subject_type = safe_str(row.get('科类'))
            batch = safe_str(row.get('批次'))
            major = safe_str(row.get('专业'))
            score = safe_int(row.get('最低分数'))
            rank = safe_int(row.get('最低位次'))
            
            if univ and score:
                results.append(('河南', year or 2025, batch, subject_type, univ, major, score, rank))
    except Exception as e:
        print(f"  SKIP professional scores: {e}")
    return results

# ============================================================
# Main import
# ============================================================
def main():
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()
    
    # Build dedup set for scorelines
    print("Building dedup key set...")
    c.execute("SELECT year, province, university_name, COALESCE(major_name,''), min_score, COALESCE(min_rank,0) FROM scorelines")
    existing = set()
    for row in c.fetchall():
        existing.add((row[0], row[1], row[2], row[3], row[4], row[5]))
    print(f"  Existing scorelines: {len(existing):,}")
    
    total_new = 0
    
    # --- Process all root scoreline files ---
    scoreline_patterns = [
        '投档线.xlsx', '投档分.xlsx', '投档情况.xlsx', '投档分数线.xlsx',
        '投档分数.xlsx', '投档情况统计.xlsx', '投档位次分数线统计表.xls',
        '投档分数线表.xls', '平行志愿投档分数.xlsx', '投档分数统计.xlsx',
        '投档最高分最低分.xlsx',
    ]
    
    root_files = [f for f in os.listdir(BASE) if f.endswith(('.xlsx', '.xls')) and '.downloading' not in f]
    
    # Also include the Jiangxi file
    all_scoreline_files = []
    for f in root_files:
        if any(pat in f for pat in scoreline_patterns) or '录取统计' in f or '招生（物理+历史）' in f:
            all_scoreline_files.append(f)
    
    print(f"\n=== Processing {len(all_scoreline_files)} scoreline files ===")
    
    for fname in sorted(all_scoreline_files):
        path = os.path.join(BASE, fname)
        prov = guess_province(fname)
        print(f"  [{prov}] {fname[:60]}...", end=' ')
        
        records = parse_scoreline_file(path, fname)
        
        if not records:
            print("0 records")
            continue
        
        new_count = 0
        batch = []
        for rec in records:
            province, year, batch_name, subject, univ, major, score, rank = rec
            key = (year, province or '', univ, major or '', score, rank or 0)
            if key in existing:
                continue
            existing.add(key)
            batch.append((univ, province, year, batch_name, score, None, None, rank, major, f'baidu_{province}'))
            
            if len(batch) >= 5000:
                c.executemany(
                    "INSERT INTO scorelines (university_name, province, year, batch, min_score, avg_score, max_score, min_rank, major_name, source) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    batch
                )
                db.commit()
                new_count += len(batch)
                batch = []
        
        if batch:
            c.executemany(
                "INSERT INTO scorelines (university_name, province, year, batch, min_score, avg_score, max_score, min_rank, major_name, source) VALUES (?,?,?,?,?,?,?,?,?,?)",
                batch
            )
            db.commit()
            new_count += len(batch)
        
        total_new += new_count
        print(f"{len(records)} parsed, {new_count} new")
    
    # --- Process Henan professional scores ---
    prof_path = os.path.join(BASE, "25年全国高校在河南的专业录取分数.xlsx")
    if os.path.exists(prof_path):
        print(f"\n=== Processing Henan professional scores ===")
        records = parse_henan_professional_scores(prof_path)
        new_count = 0
        batch = []
        for rec in records:
            province, year, batch_name, subject, univ, major, score, rank = rec
            key = (year, province, univ, major or '', score, rank or 0)
            if key in existing:
                continue
            existing.add(key)
            batch.append((univ, province, year, batch_name, score, None, None, rank, major, 'baidu_henan_prof'))
            
            if len(batch) >= 5000:
                c.executemany(
                    "INSERT INTO scorelines (university_name, province, year, batch, min_score, avg_score, max_score, min_rank, major_name, source) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    batch
                )
                db.commit()
                new_count += len(batch)
                batch = []
        
        if batch:
            c.executemany(
                "INSERT INTO scorelines (university_name, province, year, batch, min_score, avg_score, max_score, min_rank, major_name, source) VALUES (?,?,?,?,?,?,?,?,?,?)",
                batch
            )
            db.commit()
            new_count += len(batch)
        
        total_new += new_count
        print(f"  {len(records)} parsed, {new_count} new")
    
    # --- Process Henan enrollment plans ---
    enroll_path = os.path.join(BASE, "河南-2025-招生计划.xlsx")
    if os.path.exists(enroll_path):
        print(f"\n=== Processing Henan enrollment plans ===")
        records = parse_enrollment_file(enroll_path)
        
        # Import to enrollment_plans (simpler table)
        c.execute("SELECT university_name, province, year, COALESCE(major_name,''), quota FROM enrollment_plans")
        seen_plans = set()
        for row in c.fetchall():
            seen_plans.add((row[0], row[1], row[2], row[3], row[4] or 0))
        
        new_count = 0
        batch = []
        for rec in records:
            key = (rec['university_name'], rec['province'], rec['year'], rec['major_name'] or '', rec['quota'] or 0)
            if key in seen_plans:
                continue
            seen_plans.add(key)
            batch.append((rec['university_name'], rec['province'], rec['year'],
                         rec['major_name'], rec['quota'], 'baidu_henan'))
            
            if len(batch) >= 5000:
                c.executemany(
                    "INSERT INTO enrollment_plans (university_name, province, year, major_name, quota, source) VALUES (?,?,?,?,?,?)",
                    batch
                )
                db.commit()
                new_count += len(batch)
                batch = []
        
        if batch:
            c.executemany(
                "INSERT INTO enrollment_plans (university_name, province, year, major_name, quota, source) VALUES (?,?,?,?,?,?)",
                batch
            )
            db.commit()
            new_count += len(batch)
        
        # Import to enrollment_plans_detail (rich table, no year column - all 2025)
        c.execute("SELECT university_name, province, COALESCE(major_name,''), COALESCE(major_code,'') FROM enrollment_plans_detail")
        seen_detail = set()
        for row in c.fetchall():
            seen_detail.add((row[0], row[1], row[2], row[3]))
        
        detail_new = 0
        detail_batch = []
        for rec in records:
            key = (rec['university_name'], rec['province'], rec['major_name'] or '', rec['major_code'] or '')
            if key in seen_detail:
                continue
            seen_detail.add(key)
            detail_batch.append((
                rec['batch'], None, rec['university_name'],
                rec['major_group_code'], None, rec['major_code'],
                rec['major_name'], rec['subject_requirement'], rec['notes'],
                rec['duration'], rec['tuition'], None, None,
                rec['province'], None, None, None, rec['quota'],
                None, None, None, None,
                'baidu_henan'
            ))
            
            if len(detail_batch) >= 5000:
                c.executemany(
                    """INSERT INTO enrollment_plans_detail 
                    (batch, enrollment_type, university_name, major_group_code, major_group_name, 
                     major_code, major_name, subject_requirement, notes, duration, tuition,
                     school_nature, university_level, province, city, first_class_type, direct_department, plan_2025,
                     score_2024, rank_2024, score_2023, rank_2023, source)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    detail_batch
                )
                db.commit()
                detail_new += len(detail_batch)
                detail_batch = []
        
        if detail_batch:
            c.executemany(
                """INSERT INTO enrollment_plans_detail 
                (batch, enrollment_type, university_name, major_group_code, major_group_name,
                 major_code, major_name, subject_requirement, notes, duration, tuition,
                 school_nature, university_level, province, city, first_class_type, direct_department, plan_2025,
                 score_2024, rank_2024, score_2023, rank_2023, source)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                detail_batch
            )
            db.commit()
            detail_new += len(detail_batch)
        
        print(f"  enrollment_plans: {new_count} new | enrollment_plans_detail: {detail_new} new")
    
    # --- Final summary ---
    print(f"\n{'='*60}")
    print(f"IMPORT COMPLETE: {total_new:,} new scorelines")
    
    c.execute("SELECT source, COUNT(*) FROM scorelines GROUP BY source ORDER BY COUNT(*) DESC")
    for row in c.fetchall():
        print(f"  scorelines(source={row[0]}): {row[1]:,}")
    
    c.execute("SELECT COUNT(*) FROM enrollment_plans")
    print(f"  enrollment_plans: {c.fetchone()[0]:,}")
    
    c.execute("SELECT COUNT(*) FROM enrollment_plans_detail")
    print(f"  enrollment_plans_detail: {c.fetchone()[0]:,}")
    
    db.close()

if __name__ == '__main__':
    main()
