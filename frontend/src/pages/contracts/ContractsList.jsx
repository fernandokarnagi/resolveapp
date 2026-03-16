import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Edit, Trash2 } from 'lucide-react'
import api from '../../api/axios'
import DataTable from '../../components/DataTable'
import Modal from '../../components/Modal'
import StatusBadge from '../../components/StatusBadge'
import { useForm } from 'react-hook-form'

function ContractForm({ defaultValues, onSubmit, loading, clients, buildings }) {
  const { register, handleSubmit } = useForm({ defaultValues })
  const [selectedBuildings, setSelectedBuildings] = useState(defaultValues?.building_ids || [])

  const toggleBuilding = (id) => {
    setSelectedBuildings(prev =>
      prev.includes(id) ? prev.filter(b => b !== id) : [...prev, id]
    )
  }

  const submit = (data) => onSubmit({ ...data, building_ids: selectedBuildings })

  return (
    <form onSubmit={handleSubmit(submit)} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Contract Number *</label>
          <input {...register('contract_number', { required: true })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="e.g. CON-2024-001" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Client *</label>
          <select {...register('client_id', { required: true })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">Select Client</option>
            {clients.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Title *</label>
        <input {...register('title', { required: true })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Start Date *</label>
          <input type="date" {...register('start_date', { required: true })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">End Date</label>
          <input type="date" {...register('end_date')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Status</label>
          <select {...register('status')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="draft">Draft</option>
            <option value="active">Active</option>
            <option value="expired">Expired</option>
            <option value="terminated">Terminated</option>
          </select>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Contract Value</label>
          <input type="number" step="0.01" {...register('value')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Currency</label>
          <select {...register('currency')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="SGD">SGD</option>
            <option value="USD">USD</option>
            <option value="MYR">MYR</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">Buildings Covered</label>
        {buildings.length === 0 ? (
          <p className="text-xs text-slate-400">No buildings available.</p>
        ) : (
          <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto border border-slate-200 rounded-lg p-3">
            {buildings.map(b => (
              <label key={b.id} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedBuildings.includes(b.id)}
                  onChange={() => toggleBuilding(b.id)}
                  className="rounded text-blue-600"
                />
                <span className="text-sm text-slate-700 truncate">{b.name}</span>
              </label>
            ))}
          </div>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Description</label>
        <textarea {...register('description')} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
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

export default function ContractsList() {
  const qc = useQueryClient()
  const [modal, setModal] = useState(null)
  const [search, setSearch] = useState('')

  const { data = [], isLoading } = useQuery({ queryKey: ['contracts'], queryFn: () => api.get('/api/contracts').then(r => r.data) })
  const { data: clients = [] } = useQuery({ queryKey: ['clients'], queryFn: () => api.get('/api/clients').then(r => r.data) })
  const { data: buildings = [] } = useQuery({ queryKey: ['buildings'], queryFn: () => api.get('/api/buildings').then(r => r.data) })

  const createMut = useMutation({ mutationFn: d => api.post('/api/contracts', d), onSuccess: () => { qc.invalidateQueries(['contracts']); setModal(null) } })
  const updateMut = useMutation({ mutationFn: ({ id, ...d }) => api.put(`/api/contracts/${id}`, d), onSuccess: () => { qc.invalidateQueries(['contracts']); setModal(null) } })
  const deleteMut = useMutation({ mutationFn: id => api.delete(`/api/contracts/${id}`), onSuccess: () => qc.invalidateQueries(['contracts']) })

  const filtered = data.filter(c =>
    c.contract_number?.toLowerCase().includes(search.toLowerCase()) ||
    c.title?.toLowerCase().includes(search.toLowerCase()) ||
    c.client_name?.toLowerCase().includes(search.toLowerCase())
  )

  const columns = [
    { key: 'contract_number', label: 'Contract No', render: v => <span className="font-mono text-xs text-blue-600 font-semibold">{v}</span> },
    { key: 'title', label: 'Title' },
    { key: 'client_name', label: 'Client', render: v => v || '—' },
    { key: 'building_names', label: 'Buildings', render: v => (v || []).length > 0 ? <span className="text-xs">{v.join(', ')}</span> : '—' },
    { key: 'start_date', label: 'Start' },
    { key: 'end_date', label: 'End', render: v => v || '—' },
    { key: 'value', label: 'Value', render: (v, row) => v ? `${row.currency} ${Number(v).toLocaleString()}` : '—' },
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
        <div><h1 className="text-xl font-bold text-slate-800">Contracts</h1><p className="text-sm text-slate-500">{data.length} contracts</p></div>
        <button onClick={() => setModal({ type: 'create' })} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"><Plus size={16} /> Add Contract</button>
      </div>
      <DataTable columns={columns} data={filtered} loading={isLoading} onSearch={setSearch} />
      {modal && (
        <Modal title={modal.type === 'create' ? 'Add Contract' : 'Edit Contract'} onClose={() => setModal(null)} size="lg">
          <ContractForm
            defaultValues={modal.data || { status: 'active', currency: 'SGD' }}
            onSubmit={d => modal.type === 'create' ? createMut.mutate(d) : updateMut.mutate({ id: modal.data.id, ...d })}
            loading={createMut.isPending || updateMut.isPending}
            clients={clients}
            buildings={buildings}
          />
        </Modal>
      )}
    </div>
  )
}
