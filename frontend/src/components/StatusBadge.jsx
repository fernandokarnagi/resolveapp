const colorMap = {
  // Generic
  active: 'bg-green-100 text-green-700',
  inactive: 'bg-gray-100 text-gray-600',
  suspended: 'bg-red-100 text-red-700',
  // Case / Maintenance status
  open: 'bg-blue-100 text-blue-700',
  in_progress: 'bg-yellow-100 text-yellow-700',
  completed: 'bg-green-100 text-green-700',
  resolved: 'bg-teal-100 text-teal-700',
  closed: 'bg-gray-100 text-gray-600',
  cancelled: 'bg-red-100 text-red-600',
  scheduled: 'bg-indigo-100 text-indigo-700',
  overdue: 'bg-red-100 text-red-700',
  confirmed: 'bg-purple-100 text-purple-700',
  // Unit status
  occupied: 'bg-green-100 text-green-700',
  vacant: 'bg-slate-100 text-slate-600',
  maintenance: 'bg-orange-100 text-orange-700',
  // Priority
  low: 'bg-slate-100 text-slate-600',
  medium: 'bg-yellow-100 text-yellow-700',
  high: 'bg-orange-100 text-orange-700',
  critical: 'bg-red-100 text-red-700',
  // Payment
  pending: 'bg-yellow-100 text-yellow-700',
  paid: 'bg-green-100 text-green-700',
  // Attendance
  present: 'bg-green-100 text-green-700',
  absent: 'bg-red-100 text-red-700',
  late: 'bg-orange-100 text-orange-700',
  half_day: 'bg-yellow-100 text-yellow-700',
}

export default function StatusBadge({ status }) {
  const color = colorMap[status] || 'bg-gray-100 text-gray-600'
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${color}`}>
      {status?.replace(/_/g, ' ')}
    </span>
  )
}
