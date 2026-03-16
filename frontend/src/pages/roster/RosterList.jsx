import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Edit, Trash2 } from 'lucide-react'
import api from '../../api/axios'
import DataTable from '../../components/DataTable'
import Modal from '../../components/Modal'
import StatusBadge from '../../components/StatusBadge'
import { useForm } from 'react-hook-form'

function RosterForm({ defaultValues, onSubmit, loading, buildings, officers, contracts }) {
  const { register, handleSubmit, watch, setValue } = useForm({ defaultValues })
  const selectedOfficers = watch('assigned_officer_ids') || []

  const toggleOfficer = (id) => {
    const updated = selectedOfficers.includes(id)
      ? selectedOfficers.filter(o => o !== id)
      : [...selectedOfficers, id]
    setValue('assigned_officer_ids', updated)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Building *</label>
          <select {...register('building_id', { required: true })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">Select Building</option>
            {buildings.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Date *</label>
          <input type="date" {...register('date', { required: true })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Shift</label>
          <select {...register('shift')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="morning">Morning</option>
            <option value="evening">Evening</option>
            <option value="night">Night</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Start Time *</label>
          <input type="time" {...register('start_time', { required: true })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">End Time *</label>
          <input type="time" {...register('end_time', { required: true })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
      </div>

      {/* Security Officers */}
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">Security Officers</label>
        {officers.length === 0 ? (
          <p className="text-sm text-slate-400">No security officers found.</p>
        ) : (
          <div className="border border-slate-200 rounded-lg divide-y divide-slate-100 max-h-40 overflow-y-auto">
            {officers.map(o => (
              <label key={o.id} className="flex items-center gap-3 px-3 py-2 hover:bg-slate-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedOfficers.includes(o.id)}
                  onChange={() => toggleOfficer(o.id)}
                  className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-slate-700">{o.name}</span>
              </label>
            ))}
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Contract</label>
          <select {...register('contract_id')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">No Contract</option>
            {contracts.map(c => <option key={c.id} value={c.id}>{c.contract_number} – {c.title}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Status</label>
          <select {...register('status')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="scheduled">Scheduled</option>
            <option value="confirmed">Confirmed</option>
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

export default function RosterList() {
  const qc = useQueryClient()
  const [modal, setModal] = useState(null)
  const [search, setSearch] = useState('')

  const { data = [], isLoading } = useQuery({ queryKey: ['roster'], queryFn: () => api.get('/api/roster').then(r => r.data) })
  const { data: buildings = [] } = useQuery({ queryKey: ['buildings'], queryFn: () => api.get('/api/buildings').then(r => r.data) })
  const { data: users = [] } = useQuery({ queryKey: ['users'], queryFn: () => api.get('/api/users').then(r => r.data) })
  const { data: contracts = [] } = useQuery({ queryKey: ['contracts'], queryFn: () => api.get('/api/contracts').then(r => r.data) })

  const officers = users.filter(u => u.role === 'security')

  const createMut = useMutation({ mutationFn: d => api.post('/api/roster', d), onSuccess: () => { qc.invalidateQueries(['roster']); setModal(null) } })
  const updateMut = useMutation({ mutationFn: ({ id, ...d }) => api.put(`/api/roster/${id}`, d), onSuccess: () => { qc.invalidateQueries(['roster']); setModal(null) } })
  const deleteMut = useMutation({ mutationFn: id => api.delete(`/api/roster/${id}`), onSuccess: () => qc.invalidateQueries(['roster']) })

  const filtered = data.filter(r => r.building_name?.toLowerCase().includes(search.toLowerCase()))

  const columns = [
    { key: 'date', label: 'Date' },
    { key: 'building_name', label: 'Building' },
    { key: 'shift', label: 'Shift', render: v => <span className="capitalize px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded text-xs">{v}</span> },
    { key: 'start_time', label: 'Start' },
    { key: 'end_time', label: 'End' },
    { key: 'officer_names', label: 'Officers', render: v => (v || []).join(', ') || '-' },
    { key: 'contract_number', label: 'Contract', render: v => v ? <span className="font-mono text-xs text-blue-600">{v}</span> : '-' },
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
        <div><h1 className="text-xl font-bold text-slate-800">Security Roster</h1></div>
        <button onClick={() => setModal({ type: 'create' })} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"><Plus size={16} /> Add Roster</button>
      </div>
      <DataTable columns={columns} data={filtered} loading={isLoading} onSearch={setSearch} />
      {modal && (
        <Modal title={modal.type === 'create' ? 'Add Duty Roster' : 'Edit Roster'} onClose={() => setModal(null)}>
          <RosterForm
            defaultValues={modal.data || { shift: 'night', status: 'scheduled', date: new Date().toISOString().slice(0,10), assigned_officer_ids: [] }}
            onSubmit={d => modal.type === 'create' ? createMut.mutate(d) : updateMut.mutate({ id: modal.data.id, ...d })}
            loading={createMut.isPending || updateMut.isPending}
            buildings={buildings}
            officers={officers}
            contracts={contracts}
          />
        </Modal>
      )}
    </div>
  )
}
