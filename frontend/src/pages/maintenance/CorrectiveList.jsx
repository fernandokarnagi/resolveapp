import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Edit, Trash2 } from 'lucide-react'
import api from '../../api/axios'
import DataTable from '../../components/DataTable'
import Modal from '../../components/Modal'
import StatusBadge from '../../components/StatusBadge'
import { useForm, useWatch } from 'react-hook-form'

function CMForm({ defaultValues, onSubmit, loading, buildings, vendors }) {
  const { register, handleSubmit, control, setValue } = useForm({ defaultValues })
  const selectedBuildingId = useWatch({ control, name: 'building_id' })
  const selectedFloorId = useWatch({ control, name: 'floor_id' })

  const [floors, setFloors] = useState([])
  const [units, setUnits] = useState([])

  useEffect(() => {
    if (selectedBuildingId) {
      api.get(`/api/buildings/${selectedBuildingId}/floors`).then(r => {
        setFloors(r.data)
        if (!defaultValues?.floor_id) setValue('floor_id', '')
        setUnits([])
        if (!defaultValues?.unit_id) setValue('unit_id', '')
      }).catch(() => setFloors([]))
    } else {
      setFloors([])
      setUnits([])
    }
  }, [selectedBuildingId])

  useEffect(() => {
    if (selectedBuildingId && selectedFloorId) {
      api.get(`/api/buildings/${selectedBuildingId}/units?floor_id=${selectedFloorId}`).then(r => {
        setUnits(r.data)
        if (!defaultValues?.unit_id) setValue('unit_id', '')
      }).catch(() => setUnits([]))
    } else {
      setUnits([])
    }
  }, [selectedFloorId])

  // Preload floors/units when editing an existing record
  useEffect(() => {
    if (defaultValues?.building_id) {
      api.get(`/api/buildings/${defaultValues.building_id}/floors`).then(r => {
        setFloors(r.data)
        if (defaultValues?.floor_id) {
          api.get(`/api/buildings/${defaultValues.building_id}/units?floor_id=${defaultValues.floor_id}`).then(r2 => setUnits(r2.data))
        }
      })
    }
  }, [])

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
            {['electrical','plumbing','hvac','elevator','fire_safety','general','structural'].map(c => <option key={c} value={c}>{c.replace('_',' ')}</option>)}
          </select>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Floor</label>
          <select {...register('floor_id')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" disabled={!floors.length}>
            <option value="">Select Floor</option>
            {floors.map(f => <option key={f.id} value={f.id}>{f.name}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Unit</label>
          <select {...register('unit_id')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" disabled={!units.length}>
            <option value="">Select Unit</option>
            {units.map(u => <option key={u.id} value={u.id}>{u.unit_number}{u.tenant_name ? ` – ${u.tenant_name}` : ''}</option>)}
          </select>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Priority</label>
          <select {...register('priority')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="critical">Critical</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Status</label>
          <select {...register('status')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="open">Open</option><option value="in_progress">In Progress</option><option value="completed">Completed</option><option value="closed">Closed</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Reported Date *</label>
          <input type="date" {...register('reported_date', { required: true })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Reported By</label>
          <input {...register('reported_by')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Assigned Vendor</label>
          <select {...register('assigned_vendor_id')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">Select Vendor</option>
            {vendors.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
          </select>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Actual Cost (SGD)</label>
          <input type="number" step="0.01" {...register('actual_cost')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Completion Date</label>
          <input type="date" {...register('completion_date')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Description</label>
        <textarea {...register('description')} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">Resolution Notes</label>
        <textarea {...register('resolution_notes')} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div className="flex justify-end">
        <button type="submit" disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
          {loading ? 'Saving...' : 'Save'}
        </button>
      </div>
    </form>
  )
}

export default function CorrectiveList() {
  const qc = useQueryClient()
  const [modal, setModal] = useState(null)
  const [search, setSearch] = useState('')

  const { data = [], isLoading } = useQuery({ queryKey: ['cm'], queryFn: () => api.get('/api/maintenance/corrective').then(r => r.data) })
  const { data: buildings = [] } = useQuery({ queryKey: ['buildings'], queryFn: () => api.get('/api/buildings').then(r => r.data) })
  const { data: vendors = [] } = useQuery({ queryKey: ['vendors'], queryFn: () => api.get('/api/vendors').then(r => r.data) })

  const createMut = useMutation({ mutationFn: d => api.post('/api/maintenance/corrective', d), onSuccess: () => { qc.invalidateQueries(['cm']); setModal(null) } })
  const updateMut = useMutation({ mutationFn: ({ id, ...d }) => api.put(`/api/maintenance/corrective/${id}`, d), onSuccess: () => { qc.invalidateQueries(['cm']); setModal(null) } })
  const deleteMut = useMutation({ mutationFn: id => api.delete(`/api/maintenance/corrective/${id}`), onSuccess: () => qc.invalidateQueries(['cm']) })

  const filtered = data.filter(m => m.title?.toLowerCase().includes(search.toLowerCase()))

  const columns = [
    { key: 'title', label: 'Title' },
    { key: 'building_name', label: 'Building' },
    { key: 'floor_name', label: 'Floor', render: v => v || '-' },
    { key: 'unit_number', label: 'Unit', render: v => v || '-' },
    { key: 'category', label: 'Category', render: v => <span className="capitalize text-xs bg-slate-100 px-2 py-0.5 rounded">{v?.replace('_', ' ')}</span> },
    { key: 'reported_date', label: 'Reported' },
    { key: 'priority', label: 'Priority', render: v => <StatusBadge status={v} /> },
    { key: 'status', label: 'Status', render: v => <StatusBadge status={v} /> },
    { key: 'actual_cost', label: 'Cost', render: v => v ? `SGD ${v}` : '-' },
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
        <div><h1 className="text-xl font-bold text-slate-800">Corrective Maintenance</h1></div>
        <button onClick={() => setModal({ type: 'create' })} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"><Plus size={16} /> Add CM</button>
      </div>
      <DataTable columns={columns} data={filtered} loading={isLoading} onSearch={setSearch} />
      {modal && (
        <Modal title={modal.type === 'create' ? 'Add Corrective Maintenance' : 'Edit CM'} onClose={() => setModal(null)} size="lg">
          <CMForm
            defaultValues={modal.data || { category: 'general', priority: 'medium', status: 'open', reported_date: new Date().toISOString().slice(0,10) }}
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
