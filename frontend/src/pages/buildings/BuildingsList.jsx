import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Edit, Trash2 } from 'lucide-react'
import api from '../../api/axios'
import DataTable from '../../components/DataTable'
import Modal from '../../components/Modal'
import StatusBadge from '../../components/StatusBadge'
import { useForm } from 'react-hook-form'

function BuildingForm({ defaultValues, onSubmit, loading, clients }) {
  const { register, handleSubmit, formState: { errors } } = useForm({ defaultValues })
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Name *</label>
          <input {...register('name', { required: true })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Total Floors</label>
          <input type="number" {...register('total_floors')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Address *</label>
        <input {...register('address', { required: true })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Client</label>
          <select {...register('client_id')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">No Client</option>
            {clients.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Status</label>
          <select {...register('status')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="under_maintenance">Under Maintenance</option>
          </select>
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Description</label>
        <textarea {...register('description')} rows={3} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <button type="submit" disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
          {loading ? 'Saving...' : 'Save'}
        </button>
      </div>
    </form>
  )
}

export default function BuildingsList() {
  const qc = useQueryClient()
  const [modal, setModal] = useState(null)
  const [search, setSearch] = useState('')

  const { data = [], isLoading } = useQuery({
    queryKey: ['buildings'],
    queryFn: () => api.get('/api/buildings').then(r => r.data),
  })
  const { data: clients = [] } = useQuery({ queryKey: ['clients'], queryFn: () => api.get('/api/clients').then(r => r.data) })

  const createMut = useMutation({
    mutationFn: (d) => api.post('/api/buildings', d),
    onSuccess: () => { qc.invalidateQueries(['buildings']); setModal(null) },
  })
  const updateMut = useMutation({
    mutationFn: ({ id, ...d }) => api.put(`/api/buildings/${id}`, d),
    onSuccess: () => { qc.invalidateQueries(['buildings']); setModal(null) },
  })
  const deleteMut = useMutation({
    mutationFn: (id) => api.delete(`/api/buildings/${id}`),
    onSuccess: () => qc.invalidateQueries(['buildings']),
  })

  const filtered = data.filter(b =>
    b.name.toLowerCase().includes(search.toLowerCase()) ||
    b.address.toLowerCase().includes(search.toLowerCase())
  )

  const columns = [
    { key: 'name', label: 'Name' },
    { key: 'client_name', label: 'Client', render: v => v || '—' },
    { key: 'address', label: 'Address' },
    { key: 'total_floors', label: 'Floors' },
    { key: 'status', label: 'Status', render: (v) => <StatusBadge status={v} /> },
    {
      key: 'actions', label: 'Actions', render: (_, row) => (
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
        <div>
          <h1 className="text-xl font-bold text-slate-800">Buildings</h1>
          <p className="text-sm text-slate-500">{data.length} buildings</p>
        </div>
        <button onClick={() => setModal({ type: 'create' })} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
          <Plus size={16} /> Add Building
        </button>
      </div>

      <DataTable columns={columns} data={filtered} loading={isLoading} onSearch={setSearch} />

      {modal && (
        <Modal
          title={modal.type === 'create' ? 'Add Building' : 'Edit Building'}
          onClose={() => setModal(null)}
        >
          <BuildingForm
            defaultValues={modal.data || { status: 'active', total_floors: 0 }}
            onSubmit={(d) => modal.type === 'create' ? createMut.mutate(d) : updateMut.mutate({ id: modal.data.id, ...d })}
            loading={createMut.isPending || updateMut.isPending}
            clients={clients}
          />
        </Modal>
      )}
    </div>
  )
}
