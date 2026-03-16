import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Edit, Trash2, UserPlus, X } from 'lucide-react'
import api from '../../api/axios'
import DataTable from '../../components/DataTable'
import Modal from '../../components/Modal'
import StatusBadge from '../../components/StatusBadge'
import { useForm } from 'react-hook-form'

function ContactRows({ contacts, onChange }) {
  const add = () => onChange([...contacts, { name: '', role: '', email: '', phone: '' }])
  const remove = (i) => onChange(contacts.filter((_, idx) => idx !== i))
  const update = (i, field, value) => {
    const updated = contacts.map((c, idx) => idx === i ? { ...c, [field]: value } : c)
    onChange(updated)
  }
  const inputCls = 'w-full border border-slate-300 rounded px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-blue-500'
  return (
    <div className="space-y-2">
      {contacts.map((c, i) => (
        <div key={i} className="grid grid-cols-4 gap-2 items-center">
          <input value={c.name} onChange={e => update(i, 'name', e.target.value)} placeholder="Name *" className={inputCls} />
          <input value={c.role} onChange={e => update(i, 'role', e.target.value)} placeholder="Role" className={inputCls} />
          <input value={c.email} onChange={e => update(i, 'email', e.target.value)} placeholder="Email" className={inputCls} />
          <div className="flex gap-1">
            <input value={c.phone} onChange={e => update(i, 'phone', e.target.value)} placeholder="Phone" className={inputCls} />
            <button type="button" onClick={() => remove(i)} className="p-1 text-red-400 hover:text-red-600 flex-shrink-0"><X size={14} /></button>
          </div>
        </div>
      ))}
      <button type="button" onClick={add} className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 font-medium">
        <UserPlus size={13} /> Add Contact
      </button>
    </div>
  )
}

function ClientForm({ defaultValues, onSubmit, loading }) {
  const { register, handleSubmit } = useForm({ defaultValues })
  const [contacts, setContacts] = useState(defaultValues?.contacts || [])

  const submit = (data) => onSubmit({ ...data, contacts })

  return (
    <form onSubmit={handleSubmit(submit)} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Company Name *</label>
          <input {...register('name', { required: true })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Registration No.</label>
          <input {...register('registration_number')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Industry</label>
          <input {...register('industry')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Website</label>
          <input {...register('website')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="https://" />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
          <input type="email" {...register('email')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Phone</label>
          <input {...register('phone')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
      </div>

      <div className="border-t border-slate-200 pt-3">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">Address</p>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Street</label>
          <input {...register('address_street')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div className="grid grid-cols-3 gap-4 mt-3">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">City</label>
            <input {...register('address_city')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Country</label>
            <input {...register('address_country')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Postal</label>
            <input {...register('address_postal')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
        </div>
      </div>

      <div className="border-t border-slate-200 pt-3">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">Contacts</p>
        <ContactRows contacts={contacts} onChange={setContacts} />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Status</label>
          <select {...register('status')} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
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

export default function ClientsList() {
  const qc = useQueryClient()
  const [modal, setModal] = useState(null)
  const [search, setSearch] = useState('')

  const { data = [], isLoading } = useQuery({ queryKey: ['clients'], queryFn: () => api.get('/api/clients').then(r => r.data) })

  const createMut = useMutation({ mutationFn: d => api.post('/api/clients', d), onSuccess: () => { qc.invalidateQueries(['clients']); setModal(null) } })
  const updateMut = useMutation({ mutationFn: ({ id, ...d }) => api.put(`/api/clients/${id}`, d), onSuccess: () => { qc.invalidateQueries(['clients']); setModal(null) } })
  const deleteMut = useMutation({ mutationFn: id => api.delete(`/api/clients/${id}`), onSuccess: () => qc.invalidateQueries(['clients']) })

  const filtered = data.filter(c =>
    c.name?.toLowerCase().includes(search.toLowerCase()) ||
    c.email?.toLowerCase().includes(search.toLowerCase())
  )

  const columns = [
    { key: 'name', label: 'Company' },
    { key: 'industry', label: 'Industry', render: v => v || '—' },
    { key: 'email', label: 'Email', render: v => v || '—' },
    { key: 'phone', label: 'Phone', render: v => v || '—' },
    { key: 'address_city', label: 'City', render: v => v || '—' },
    { key: 'contacts', label: 'Contacts', render: v => <span className="text-xs bg-slate-100 px-2 py-0.5 rounded">{(v || []).length}</span> },
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
        <div><h1 className="text-xl font-bold text-slate-800">Clients</h1><p className="text-sm text-slate-500">{data.length} clients</p></div>
        <button onClick={() => setModal({ type: 'create' })} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"><Plus size={16} /> Add Client</button>
      </div>
      <DataTable columns={columns} data={filtered} loading={isLoading} onSearch={setSearch} />
      {modal && (
        <Modal title={modal.type === 'create' ? 'Add Client' : 'Edit Client'} onClose={() => setModal(null)} size="lg">
          <ClientForm
            defaultValues={modal.data || { status: 'active' }}
            onSubmit={d => modal.type === 'create' ? createMut.mutate(d) : updateMut.mutate({ id: modal.data.id, ...d })}
            loading={createMut.isPending || updateMut.isPending}
          />
        </Modal>
      )}
    </div>
  )
}
