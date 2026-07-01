const API_BASE = "http://localhost:8005/api";

export interface RecommendResult {
  name: string;
  province: string;
  type: string;
  level: string;
  latest_score: number | null;
  avg_rank: number;
  tier: "冲" | "稳" | "保";
  probability: number;
  majors?: number;
  rank_years?: number;
  rank_stability?: string;
  tags?: string[];
}

export interface TrendData {
  year: number;
  min_score: number | null;
  min_rank: number | null;
}

export interface CompareData {
  info: { name: string; province: string; type: string; level: string; ruanke_rank: string | null; recommend_master_rate: string };
  scores: TrendData[];
  plans: { major_count: number; total_quota: number };
}

export interface StatsData {
  universities: number;
  scorelines: number;
  provinces: number;
  years: number;
  latest_year: number;
  top: { n985: number; n211: number; n_dc: number };
}

export interface UniversityResult {
  name: string;
  province: string;
  type: string;
  level: string;
  ruanke_rank: number | null;
  tags: string[];
}

export async function fetchStats(): Promise<StatsData> {
  const res = await fetch(`${API_BASE}/stats`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function searchUniversities(q: string): Promise<UniversityResult[]> {
  if (!q.trim()) return [];
  const res = await fetch(`${API_BASE}/universities/search?q=${encodeURIComponent(q)}`);
  if (!res.ok) return [];
  const data = await res.json();
  return data.results || [];
}

export async function fetchRecommend(score: number, province: string, subject: string): Promise<{ score: number; province: string; subject: string; rank: number | null; results: RecommendResult[]; errors?: string[] }> {
  const res = await fetch(`${API_BASE}/recommend?score=${score}&province=${encodeURIComponent(province)}&subject=${encodeURIComponent(subject)}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function fetchMultiTrends(universities: string[], province: string): Promise<{ data: Record<string, TrendData[]> }> {
  const res = await fetch(`${API_BASE}/trends/multi?universities=${encodeURIComponent(universities.join(","))}&province=${encodeURIComponent(province)}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function fetchCompare(universities: string[], province: string): Promise<{ data: Record<string, CompareData> }> {
  const res = await fetch(`${API_BASE}/compare?universities=${encodeURIComponent(universities.join(","))}&province=${encodeURIComponent(province)}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export interface ScoreTrendData {
  year: number;
  avg_score: number | null;
  min_score: number | null;
  max_score: number | null;
  avg_rank: number | null;
  major_count: number;
}

export async function fetchScoreTrend(university: string, province: string): Promise<{
  trend: ScoreTrendData[];
  volatility: number | null;
  trend_direction: string;
  year_span: number;
}> {
  const res = await fetch(`${API_BASE}/analysis/score-trend?university=${encodeURIComponent(university)}&province=${encodeURIComponent(province)}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export interface EnrollmentPlanData {
  major: string;
  plan_2025: number;
  score_2024: number | null;
  rank_2024: number | null;
  score_2023: number | null;
  rank_2023: number | null;
  score_2022: number | null;
  rank_2022: number | null;
  score_change: number | null;
  postgrad_rate: string | null;
  tuition: string | null;
  subject: string | null;
}

export async function fetchEnrollmentPlans(university: string, province: string): Promise<{
  total_plan_2025: number;
  major_count: number;
  plans: EnrollmentPlanData[];
}> {
  const res = await fetch(`${API_BASE}/analysis/enrollment-plans?university=${encodeURIComponent(university)}&province=${encodeURIComponent(province)}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export interface MajorRankData {
  rank: number;
  major: string;
  lowest_score: number | null;
  best_rank: number | null;
  year_count: number;
}

export async function fetchMajorRanking(university: string, province: string): Promise<{ majors: MajorRankData[] }> {
  const res = await fetch(`${API_BASE}/analysis/major-ranking?university=${encodeURIComponent(university)}&province=${encodeURIComponent(province)}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export interface UniversityQualityData {
  name: string;
  province: string;
  type: string;
  level: string;
  is_985: boolean;
  is_211: boolean;
  is_dual_class: boolean;
  rankings: { ruanke: number | null; qs: number | null; xyh: number | null };
  academic: { master_programs: number | null; doctor_programs: number | null; academicians: number | null; postgrad_rate: string | null };
  campus: { area_mu: number | null; founded: number | null };
}

export async function fetchUniversityQuality(university: string): Promise<UniversityQualityData> {
  const res = await fetch(`${API_BASE}/analysis/university-quality?university=${encodeURIComponent(university)}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
