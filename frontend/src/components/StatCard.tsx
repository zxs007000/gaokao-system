interface StatCardProps {
  title: string;
  value: string | number;
  icon: string;
  color?: string;
}

export default function StatCard({ title, value, icon, color = "text-neon-green" }: StatCardProps) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm">{title}</p>
          <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
        </div>
        <span className="text-3xl">{icon}</span>
      </div>
    </div>
  );
}
