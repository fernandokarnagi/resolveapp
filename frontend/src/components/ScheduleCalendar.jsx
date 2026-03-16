import { useState, useMemo } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'

const MONTH_NAMES = ['January','February','March','April','May','June','July','August','September','October','November','December']
const DAY_HEADERS = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
const DAY_MAP = { sunday:0, monday:1, tuesday:2, wednesday:3, thursday:4, friday:5, saturday:6 }

// Deterministic colour per item id
const COLOURS = ['bg-blue-500','bg-green-500','bg-purple-500','bg-orange-500','bg-teal-500','bg-red-400','bg-indigo-500','bg-pink-500']
function colourFor(id = '') {
  const n = id.split('').reduce((a, c) => a + c.charCodeAt(0), 0)
  return COLOURS[n % COLOURS.length]
}

function toDateStr(date) {
  return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`
}

function occursOnDay(item, date, type) {
  const d   = date.getDate()
  const dow = date.getDay()
  const ds  = toDateStr(date)

  if (type === 'cleaning') {
    if (item.start_date && ds < item.start_date) return false
    if (item.end_date   && ds > item.end_date)   return false
    const freq = item.frequency
    if (freq === 'daily') return true
    if (freq === 'weekly' || freq === 'biweekly') {
      const days = item.schedule_days || []
      if (!days.some(day => DAY_MAP[day] === dow)) return false
      if (freq === 'biweekly' && item.start_date) {
        const diffDays = Math.round((date - new Date(item.start_date)) / 86400000)
        if (Math.floor(Math.max(diffDays, 0) / 7) % 2 !== 0) return false
      }
      return true
    }
    if (freq === 'monthly') return (item.schedule_dates || []).includes(d)
    return false
  }

  if (type === 'pm') {
    if (!item.next_due_date) return false
    const base = new Date(item.next_due_date)
    base.setHours(0,0,0,0)
    if (date < base) return false
    if (date.getDate() !== base.getDate()) return false
    const freq = item.frequency
    let step // months
    if      (freq === 'monthly')   step = 1
    else if (freq === 'quarterly') step = 3
    else if (freq === 'biannual')  step = 6
    else if (freq === 'yearly')    step = 12
    else return false
    const monthsDiff = (date.getFullYear() - base.getFullYear()) * 12 + (date.getMonth() - base.getMonth())
    return monthsDiff % step === 0
  }

  return false
}

export default function ScheduleCalendar({ items, type, buildings, vendors }) {
  const today = new Date()
  const [year,  setYear]  = useState(today.getFullYear())
  const [month, setMonth] = useState(today.getMonth())
  const [filterBuilding, setFilterBuilding] = useState('')
  const [filterVendor,   setFilterVendor]   = useState('')
  const [selected, setSelected] = useState(null)

  const filtered = useMemo(() => items.filter(item => {
    if (filterBuilding && item.building_id !== filterBuilding) return false
    if (filterVendor   && item.assigned_vendor_id !== filterVendor) return false
    return true
  }), [items, filterBuilding, filterVendor])

  const firstDow     = new Date(year, month, 1).getDay()
  const daysInMonth  = new Date(year, month + 1, 0).getDate()

  const cells = useMemo(() => {
    const result = []
    for (let i = 0; i < firstDow; i++) result.push(null)
    for (let d = 1; d <= daysInMonth; d++) {
      const date   = new Date(year, month, d)
      const events = filtered.filter(item => occursOnDay(item, date, type))
      result.push({ day: d, date, events })
    }
    return result
  }, [filtered, year, month, firstDow, daysInMonth, type])

  const prev = () => {
    setSelected(null)
    if (month === 0) { setMonth(11); setYear(y => y - 1) } else setMonth(m => m - 1)
  }
  const next = () => {
    setSelected(null)
    if (month === 11) { setMonth(0); setYear(y => y + 1) } else setMonth(m => m + 1)
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      {/* Toolbar */}
      <div className="px-4 py-3 border-b border-slate-200 flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-1">
          <button onClick={prev} className="p-1.5 rounded hover:bg-slate-100"><ChevronLeft size={16} /></button>
          <span className="text-sm font-semibold text-slate-800 w-40 text-center">{MONTH_NAMES[month]} {year}</span>
          <button onClick={next} className="p-1.5 rounded hover:bg-slate-100"><ChevronRight size={16} /></button>
        </div>
        <select
          value={filterBuilding}
          onChange={e => { setFilterBuilding(e.target.value); setSelected(null) }}
          className="text-sm border border-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Buildings</option>
          {buildings.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
        </select>
        {vendors && (
          <select
            value={filterVendor}
            onChange={e => { setFilterVendor(e.target.value); setSelected(null) }}
            className="text-sm border border-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Vendors</option>
            {vendors.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
          </select>
        )}
      </div>

      {/* Day-of-week headers */}
      <div className="grid grid-cols-7 border-b border-slate-100 bg-slate-50">
        {DAY_HEADERS.map(h => (
          <div key={h} className="py-2 text-center text-xs font-semibold text-slate-400 uppercase tracking-wide">{h}</div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="grid grid-cols-7">
        {cells.map((cell, i) => {
          const isToday    = cell && toDateStr(cell.date) === toDateStr(today)
          const isSelected = selected && cell && toDateStr(cell.date) === toDateStr(selected.date)
          return (
            <div
              key={i}
              onClick={() => cell?.events.length && setSelected(isSelected ? null : cell)}
              className={`min-h-[88px] p-1.5 border-b border-r border-slate-100 transition-colors
                ${cell?.events.length ? 'cursor-pointer hover:bg-slate-50' : ''}
                ${isSelected ? 'bg-blue-50' : ''}
              `}
            >
              {cell && (
                <>
                  <div className={`text-xs font-semibold w-6 h-6 flex items-center justify-center rounded-full mb-1
                    ${isToday ? 'bg-blue-600 text-white' : 'text-slate-500'}`}>
                    {cell.day}
                  </div>
                  <div className="space-y-0.5">
                    {cell.events.slice(0, 3).map((ev, j) => (
                      <div key={j} className={`text-white text-[10px] leading-tight px-1 py-0.5 rounded truncate ${colourFor(ev.id)}`}>
                        {ev.title}
                      </div>
                    ))}
                    {cell.events.length > 3 && (
                      <div className="text-[10px] text-slate-400 pl-1">+{cell.events.length - 3} more</div>
                    )}
                  </div>
                </>
              )}
            </div>
          )
        })}
      </div>

      {/* Selected-day detail panel */}
      {selected && (
        <div className="px-4 py-3 border-t border-slate-200 bg-slate-50">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
            {selected.date.toLocaleDateString('en-SG', { weekday:'long', day:'numeric', month:'long', year:'numeric' })}
          </p>
          <div className="space-y-2">
            {selected.events.map((ev, i) => (
              <div key={i} className="flex items-start gap-2 text-sm">
                <span className={`mt-1.5 w-2 h-2 rounded-full flex-shrink-0 ${colourFor(ev.id)}`} />
                <div className="text-slate-700">
                  <span className="font-medium">{ev.title}</span>
                  {ev.building_name && <span className="text-slate-400"> · {ev.building_name}</span>}
                  {ev.vendor_name   && <span className="text-slate-400"> · {ev.vendor_name}</span>}
                  {ev.start_time    && <span className="text-slate-400"> · {ev.start_time}{ev.duration_minutes ? ` (${ev.duration_minutes} min)` : ''}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
