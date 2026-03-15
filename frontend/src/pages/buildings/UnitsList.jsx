import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Edit, Trash2 } from 'lucide-react'
import api from '../../api/axios'
import DataTable from '../../components/DataTable'
import Modal from '../../components/Modal'
import StatusBadge from '../../components/StatusBadge'
import { useForm } from 'react-hook-form'

export default function UnitsList() {
  const qc = useQueryClient()
  const [modal, setModal] = useState(null)
  const [selectedBuilding, setSelectedBuilding] = useState('')
  const [search, setSearch] = useState('')

  const { data: buildings = [] } = useQuery({ queryKey: ['buildings'], queryFn: () => api.get('/api/buildings').then(r => r.data) })
  const { data: units = [], isLoading } = useQuery({
    queryKey: ['units', selectedBuilding],
    queryFn: () => selectedBuilding ? api.get(`/api/buildings/${selectedBuilding}/units`).then(r => r.data) : Promise.resolve([]),
    enabled: !!selectedBuilding,
  })
  const { data: floors = [] } = useQuery({
    queryKey: ['floors', selectedBuilding],
    queryFn: () => selectedBuilding ? api.get(`/api/buildings/${selectedBuilding}/floors`).then(r => r.data) : Promise.resolve([]),
    enabled: !!selectedBuilding,
  })

  const createMut = useMutation({ mutationFn: (d) => api.post(`/api/buildings/${selectedBuilding}/units`, d), onSuccess: () => { qc.invalidateQueries(['units']); setModal(null) } })
  const updateMut = useMutation({ mutationFn: ({ id, ...d }) => api.put(`/api/buildings/units/${id}`, d), onSuccess: () => { qc.invalidateQueries(['units']); setModal(null) } })
  const deleteMut = useMutation({ mutationFn: (id) => api.delete(`/api/buildings/units/${id}`), onSuccess: () => qc.invalidateQueries(['units']) })

  const filtered = units.filter(u => u.unit_number?.toLowerCase().includes(search.toLowerCase()))

  const columns = [
    { key: 'unit_number', label: 'Unit No' },
    { key: 'floor_name', label: 'Floor' },
    { key: 'type', label: 'Type', render: v => <span className="capitalize">{v}</span> },
    { key: 'status', label: 'Status', render: v => <StatusBadge status={v} /> },
    { key: 'area_sqft', label: 'Area (sqft)' },
    { key: 'tenant_name', label: 'Tenant' },
    {
      key: 'actions', label: 'Actions', render: (_, row) => (
        <div className="flex gap-2">
          <button onClick={() => setModal({ type: 'edit', data: row })} className="p-1.5 rounded hover:bg-slate-100 text-slate-500"><Edit size={15} /></button>
          <button onClick={() => { if (confirm('Delete?')) deleteMut.mutate(row.id) }} className="p-1.5 rounded hover:bg-red-50 text-red-500"><Trash2 size={15} /></button>
        </div>
      )
    }
  ]

  function UnitForm({ defaultValues, onSubmit, loading }) {
    const { register, handleSubmit } = useForm({ defaultValues })
    return (
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Unit Number *</label>
            <input {...register('unit_number', { required: true })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Floor *</label>
            <select {...register('floor_id', { required: true })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">Select Floor</option>
              {floors.map(f => <option key={f.id} value={f.id}>{f.name}</option>)}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Type</label>
            <select {...register('type')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="residential">Residential</option>
              <option value="commercial">Commercial</option>
              <option value="common">Common</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Status</label>
            <select {...register('status')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="vacant">Vacant</option>
              <option value="occupied">Occupied</option>
              <option value="maintenance">Maintenance</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Area (sqft)</label>
            <input type="number" {...register('area_sqft')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Tenant Name</label>
            <input {...register('tenant_name')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Tenant Contact</label>
            <input {...register('tenant_contact')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
        </div>
        <div className="flex justify-end">
          <button type="submit" disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
            {loading ? 'Saving...' : 'Save'}
          </button>
        </div>
      </form>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-800">Units</h1>
        <div className="flex items-center gap-3">
          <select value={selectedBuilding} onChange={e => setSelectedBuilding(e.target.value)} className="border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">Select Building</option>
            {buildings.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
          </select>
          {selectedBuilding && (
            <button onClick={() => setModal({ type: 'create' })} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
              <Plus size={16} /> Add Unit
            </button>
          )}
        </div>
      </div>
      <DataTable columns={columns} data={filtered} loading={isLoading && !!selectedBuilding} onSearch={setSearch} />
      {modal && (
        <Modal title={modal.type === 'create' ? 'Add Unit' : 'Edit Unit'} onClose={() => setModal(null)}>
          <UnitForm
            defaultValues={modal.data || { building_id: selectedBuilding, status: 'vacant', type: 'residential' }}
            onSubmit={(d) => modal.type === 'create' ? createMut.mutate(d) : updateMut.mutate({ id: modal.data.id, ...d })}
            loading={createMut.isPending || updateMut.isPending}
          />
        </Modal>
      )}
    </div>
  )
}
