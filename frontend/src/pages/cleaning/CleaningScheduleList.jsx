import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Edit, Trash2 } from 'lucide-react'
import api from '../../api/axios'
import DataTable from '../../components/DataTable'
import Modal from '../../components/Modal'
import StatusBadge from '../../components/StatusBadge'
import { useForm } from 'react-hook-form'

const DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
const DAY_LABELS = { monday: 'Mon', tuesday: 'Tue', wednesday: 'Wed', thursday: 'Thu', friday: 'Fri', saturday: 'Sat', sunday: 'Sun' }

function CleaningForm({ defaultValues, onSubmit, loading, buildings, vendors }) {
  const { register, handleSubmit, watch, setValue } = useForm({
    defaultValues: {
      schedule_days: [],
      schedule_dates: [],
      ...defaultValues,
    }
  })

  const frequency = watch('frequency')
  const scheduleDays = watch('schedule_days') || []
  const scheduleDates = watch('schedule_dates') || []

  const toggleDay = (day) => {
    const updated = scheduleDays.includes(day)
      ? scheduleDays.filter(d => d !== day)
      : [...scheduleDays, day]
    setValue('schedule_days', updated)
  }

  const toggleDate = (date) => {
    const updated = scheduleDates.includes(date)
      ? scheduleDates.filter(d => d !== date)
      : [...scheduleDates, date]
    setValue('schedule_dates', updated)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Title *</label>
        <input {...register('title', { required: true })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Building *</label>
          <select {...register('building_id', { required: true })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">Select Building</option>
            {buildings.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Assigned Vendor</label>
          <select {...register('assigned_vendor_id')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">Select Vendor</option>
            {vendors.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
          </select>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Frequency</label>
          <select {...register('frequency')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="biweekly">Bi-weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Start Date *</label>
          <input type="date" {...register('start_date', { required: true })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">End Date</label>
          <input type="date" {...register('end_date')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
      </div>

      {/* Start Time & Duration */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Start Time</label>
          <input type="time" {...register('start_time')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Duration (minutes)</label>
          <input type="number" min={1} {...register('duration_minutes', { valueAsNumber: true })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="e.g. 60" />
        </div>
      </div>

      {/* Day selector for weekly / bi-weekly */}
      {(frequency === 'weekly' || frequency === 'biweekly') && (
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Days of Week</label>
          <div className="flex flex-wrap gap-2">
            {DAYS.map(day => (
              <button
                key={day}
                type="button"
                onClick={() => toggleDay(day)}
                className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                  scheduleDays.includes(day)
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {DAY_LABELS[day]}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Date selector for monthly */}
      {frequency === 'monthly' && (
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">Dates of Month</label>
          <div className="grid grid-cols-7 gap-1">
            {Array.from({ length: 31 }, (_, i) => i + 1).map(n => (
              <button
                key={n}
                type="button"
                onClick={() => toggleDate(n)}
                className={`py-1.5 rounded text-xs font-medium transition-colors ${
                  scheduleDates.includes(n)
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {n}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Status</label>
          <select {...register('status')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="scheduled">Scheduled</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Notes</label>
        <textarea {...register('notes')} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div className="flex justify-end">
        <button type="submit" disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
          {loading ? 'Saving...' : 'Save'}
        </button>
      </div>
    </form>
  )
}

export default function CleaningScheduleList() {
  const qc = useQueryClient()
  const [modal, setModal] = useState(null)
  const [search, setSearch] = useState('')

  const { data = [], isLoading } = useQuery({ queryKey: ['cleaning'], queryFn: () => api.get('/api/cleaning').then(r => r.data) })
  const { data: buildings = [] } = useQuery({ queryKey: ['buildings'], queryFn: () => api.get('/api/buildings').then(r => r.data) })
  const { data: vendors = [] } = useQuery({ queryKey: ['vendors'], queryFn: () => api.get('/api/vendors').then(r => r.data) })

  const createMut = useMutation({ mutationFn: d => api.post('/api/cleaning', d), onSuccess: () => { qc.invalidateQueries(['cleaning']); setModal(null) } })
  const updateMut = useMutation({ mutationFn: ({ id, ...d }) => api.put(`/api/cleaning/${id}`, d), onSuccess: () => { qc.invalidateQueries(['cleaning']); setModal(null) } })
  const deleteMut = useMutation({ mutationFn: id => api.delete(`/api/cleaning/${id}`), onSuccess: () => qc.invalidateQueries(['cleaning']) })

  const filtered = data.filter(s => s.title?.toLowerCase().includes(search.toLowerCase()))

  const columns = [
    { key: 'title', label: 'Title' },
    { key: 'building_name', label: 'Building' },
    { key: 'vendor_name', label: 'Vendor' },
    { key: 'frequency', label: 'Frequency', render: v => <span className="capitalize">{v}</span> },
    { key: 'start_date', label: 'Start Date' },
    { key: 'start_time', label: 'Time', render: v => v || '—' },
    { key: 'duration_minutes', label: 'Duration', render: v => v ? `${v} min` : '—' },
    { key: 'status', label: 'Status', render: v => <StatusBadge status={v} /> },
    {
      key: 'actions', label: '', render: (_, row) => (
        <div className="flex gap-2">
          <button onClick={() => setModal({ type: 'edit', data: row })} className="p-1.5 rounded hover:bg-slate-100 text-slate-500"><Edit size={15} /></button>
          <button onClick={() => { if (confirm('Delete?')) deleteMut.mutate(row.id) }} className="p-1.5 rounded hover:bg-red-50 text-red-500"><Trash2 size={15} /></button>
        </div>
      )
    }
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div><h1 className="text-xl font-bold text-slate-800">Cleaning Schedule</h1></div>
        <button onClick={() => setModal({ type: 'create' })} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"><Plus size={16} /> Add Schedule</button>
      </div>
      <DataTable columns={columns} data={filtered} loading={isLoading} onSearch={setSearch} />
      {modal && (
        <Modal title={modal.type === 'create' ? 'Add Schedule' : 'Edit Schedule'} onClose={() => setModal(null)} size="lg">
          <CleaningForm
            defaultValues={modal.data || { frequency: 'daily', status: 'scheduled' }}
            onSubmit={d => modal.type === 'create' ? createMut.mutate(d) : updateMut.mutate({ id: modal.data.id, ...d })}
            loading={createMut.isPending || updateMut.isPending}
            buildings={buildings}
            vendors={vendors}
          />
        </Modal>
      )}
    </div>
  )
}
