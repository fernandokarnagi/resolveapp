import { useQuery } from '@tanstack/react-query'
import api from '../api/axios'
import { Building2, AlertCircle, Wrench, DollarSign, Users, CalendarCheck, TrendingUp, Clock } from 'lucide-react'
import StatusBadge from '../components/StatusBadge'
import LoadingSpinner from '../components/LoadingSpinner'

function StatCard({ label, value, icon: Icon, color, sub }) {
  return (
    <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-500 font-medium">{label}</p>
          <p className="text-3xl font-bold text-slate-800 mt-1">{value ?? '—'}</p>
          {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
        </div>
        <div className={`p-3 rounded-xl ${color}`}>
          <Icon size={22} className="text-white" />
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => api.get('/api/analytics/dashboard').then(r => r.data),
  })
  const { data: recentCases } = useQuery({
    queryKey: ['recent-cases'],
    queryFn: () => api.get('/api/analytics/recent-cases').then(r => r.data),
  })

  if (isLoading) return <LoadingSpinner />

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
        <p className="text-slate-500 text-sm mt-0.5">Facility Management Overview</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Buildings" value={stats?.total_buildings} icon={Building2} color="bg-blue-500" />
        <StatCard
          label="Occupancy Rate"
          value={`${stats?.occupancy_rate ?? 0}%`}
          icon={TrendingUp}
          color="bg-green-500"
          sub={`${stats?.occupied_units}/${stats?.total_units} units`}
        />
        <StatCard label="Open Cases" value={stats?.open_cases} icon={AlertCircle} color="bg-orange-500" />
        <StatCard
          label="Monthly Cost"
          value={`RM ${(stats?.monthly_cost ?? 0).toLocaleString()}`}
          icon={DollarSign}
          color="bg-purple-500"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Open Corrective Maintenance" value={stats?.open_corrective_maintenance} icon={Wrench} color="bg-red-500" />
        <StatCard label="Overdue PM" value={stats?.overdue_preventive_maintenance} icon={Clock} color="bg-yellow-500" />
        <StatCard label="Active Vendors" value={stats?.active_vendors} icon={Users} color="bg-teal-500" />
        <StatCard label="Total Units" value={stats?.total_units} icon={CalendarCheck} color="bg-indigo-500" />
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200">
        <div className="px-5 py-4 border-b border-slate-200">
          <h2 className="font-semibold text-slate-800">Recent Cases</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Case No</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Title</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Building</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Priority</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(recentCases || []).map(c => (
                <tr key={c.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-mono text-xs text-blue-600">{c.case_number}</td>
                  <td className="px-4 py-3 text-slate-700">{c.title}</td>
                  <td className="px-4 py-3 text-slate-500">{c.building_name || '-'}</td>
                  <td className="px-4 py-3"><StatusBadge status={c.priority} /></td>
                  <td className="px-4 py-3"><StatusBadge status={c.status} /></td>
                </tr>
              ))}
              {(!recentCases || recentCases.length === 0) && (
                <tr><td colSpan={5} className="px-4 py-6 text-center text-slate-400">No recent cases</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
