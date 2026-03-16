import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Edit, Trash2, List, CalendarDays } from 'lucide-react'
import api from '../../api/axios'
import DataTable from '../../components/DataTable'
import Modal from '../../components/Modal'
import StatusBadge from '../../components/StatusBadge'
import ScheduleCalendar from '../../components/ScheduleCalendar'
import { useForm } from 'react-hook-form'

function PMForm({ defaultValues, onSubmit, loading, buildings, vendors, contracts }) {
  const { register, handleSubmit, watch, setValue } = useForm({
    defaultValues: {
      schedule_dates: [],
      ...defaultValues,
    }
  })

  const frequency = watch('frequency')
  const scheduleDates = watch('schedule_dates') || []

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
          <label className="block text-sm font-medium text-slate-700 mb-1">Category</label>
          <select {...register('category')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            {['electrical','plumbing','hvac','elevator','fire_safety','general','structural'].map(c => <option key={c} value={c} className="capitalize">{c.replace('_',' ')}</option>)}
          </select>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Frequency</label>
          <select {...register('frequency')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="monthly">Monthly</option>
            <option value="quarterly">Quarterly</option>
            <option value="biannual">Bi-annual</option>
            <option value="yearly">Yearly</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Next Due Date *</label>
          <input type="date" {...register('next_due_date', { required: true })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Priority</label>
          <select {...register('priority')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
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
          <input type="number" min={1} {...register('duration_minutes', { valueAsNumber: true })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="e.g. 120" />
        </div>
      </div>

      {/* Date selector for monthly frequency */}
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
          <label className="block text-sm font-medium text-slate-700 mb-1">Contract</label>
          <select {...register('contract_id')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">No Contract</option>
            {contracts.map(c => <option key={c.id} value={c.id}>{c.contract_number} – {c.title}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Assigned Vendor</label>
          <select {...register('assigned_vendor_id')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">Select Vendor</option>
            {vendors.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Estimated Cost (SGD)</label>
          <input type="number" step="0.01" {...register('estimated_cost')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Description</label>
        <textarea {...register('description')} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div className="flex justify-end">
        <button type="submit" disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
          {loading ? 'Saving...' : 'Save'}
        </button>
      </div>
    </form>
  )
}

export default function PreventiveList() {
  const qc = useQueryClient()
  const [modal, setModal] = useState(null)
  const [search, setSearch] = useState('')
  const [view, setView] = useState('list')

  const { data = [], isLoading } = useQuery({ queryKey: ['pm'], queryFn: () => api.get('/api/maintenance/preventive').then(r => r.data) })
  const { data: buildings = [] } = useQuery({ queryKey: ['buildings'], queryFn: () => api.get('/api/buildings').then(r => r.data) })
  const { data: vendors = [] } = useQuery({ queryKey: ['vendors'], queryFn: () => api.get('/api/vendors').then(r => r.data) })
  const { data: contracts = [] } = useQuery({ queryKey: ['contracts'], queryFn: () => api.get('/api/contracts').then(r => r.data) })

  const createMut = useMutation({ mutationFn: d => api.post('/api/maintenance/preventive', d), onSuccess: () => { qc.invalidateQueries(['pm']); setModal(null) } })
  const updateMut = useMutation({ mutationFn: ({ id, ...d }) => api.put(`/api/maintenance/preventive/${id}`, d), onSuccess: () => { qc.invalidateQueries(['pm']); setModal(null) } })
  const deleteMut = useMutation({ mutationFn: id => api.delete(`/api/maintenance/preventive/${id}`), onSuccess: () => qc.invalidateQueries(['pm']) })

  const filtered = data.filter(m => m.title?.toLowerCase().includes(search.toLowerCase()))

  const columns = [
    { key: 'title', label: 'Title' },
    { key: 'building_name', label: 'Building' },
    { key: 'category', label: 'Category', render: v => <span className="capitalize text-xs bg-slate-100 px-2 py-0.5 rounded">{v?.replace('_', ' ')}</span> },
    { key: 'next_due_date', label: 'Next Due' },
    { key: 'frequency', label: 'Frequency', render: v => <span className="capitalize">{v}</span> },
    { key: 'start_time', label: 'Time', render: v => v || '—' },
    { key: 'duration_minutes', label: 'Duration', render: v => v ? `${v} min` : '—' },
    { key: 'priority', label: 'Priority', render: v => <StatusBadge status={v} /> },
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
        <div><h1 className="text-xl font-bold text-slate-800">Preventive Maintenance</h1></div>
        <div className="flex items-center gap-2">
          <div className="flex rounded-lg border border-slate-200 overflow-hidden">
            <button onClick={() => setView('list')} className={`px-3 py-2 text-sm flex items-center gap-1.5 ${view === 'list' ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'}`}><List size={14} /> List</button>
            <button onClick={() => setView('calendar')} className={`px-3 py-2 text-sm flex items-center gap-1.5 ${view === 'calendar' ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'}`}><CalendarDays size={14} /> Calendar</button>
          </div>
          <button onClick={() => setModal({ type: 'create' })} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"><Plus size={16} /> Add PM</button>
        </div>
      </div>
      {view === 'calendar'
        ? <ScheduleCalendar items={data} type="pm" buildings={buildings} vendors={vendors} />
        : <DataTable columns={columns} data={filtered} loading={isLoading} onSearch={setSearch} />
      }
      {modal && (
        <Modal title={modal.type === 'create' ? 'Add Preventive Maintenance' : 'Edit PM'} onClose={() => setModal(null)} size="lg">
          <PMForm
            defaultValues={modal.data || { category: 'general', frequency: 'monthly', priority: 'medium', status: 'scheduled' }}
            onSubmit={d => modal.type === 'create' ? createMut.mutate(d) : updateMut.mutate({ id: modal.data.id, ...d })}
            loading={createMut.isPending || updateMut.isPending}
            buildings={buildings}
            vendors={vendors}
            contracts={contracts}
          />
        </Modal>
      )}
    </div>
  )
}
