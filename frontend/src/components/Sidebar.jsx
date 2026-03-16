import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Building2, Users, ShoppingBag, CalendarCheck,
  Wrench, AlertTriangle, PhoneCall, DollarSign, Moon, ClipboardCheck,
  Shield, BarChart2, ChevronDown, ChevronRight, Building, Settings,
  ClipboardList, Zap, Eye, X
} from 'lucide-react'
import { useState } from 'react'

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  {
    label: 'Planning', icon: ClipboardList, children: [
      { to: '/cleaning',                label: 'Cleaning Schedule',       icon: CalendarCheck },
      { to: '/maintenance/preventive',  label: 'Preventive Maintenance',  icon: Wrench },
      { to: '/roster',                  label: 'Night Watch Roster',       icon: Moon },
    ]
  },
  {
    label: 'Action', icon: Zap, children: [
      { to: '/maintenance/corrective',  label: 'Corrective Maintenance',  icon: AlertTriangle },
      { to: '/cases',                   label: 'Cases & Calls',           icon: PhoneCall },
    ]
  },
  {
    label: 'Observe', icon: Eye, children: [
      { to: '/costs',     label: 'Cost Management', icon: DollarSign },
      { to: '/analytics', label: 'Analytics',       icon: BarChart2 },
    ]
  },
  {
    label: 'Attendance', icon: ClipboardCheck, children: [
      { to: '/attendance/cleaner',  label: 'Cleaner',  icon: ClipboardCheck },
      { to: '/attendance/security', label: 'Security', icon: Shield },
    ]
  },
  {
    label: 'Administration', icon: Settings, children: [
      { to: '/buildings', label: 'Buildings',         icon: Building2 },
      { to: '/floors',    label: 'Floors',            icon: Building },
      { to: '/units',     label: 'Units',             icon: Building },
      { to: '/users',     label: 'Users',             icon: Users },
      { to: '/vendors',   label: 'Vendors & Cleaners',icon: ShoppingBag },
    ]
  },
]

function NavItem({ item, collapsed, onNavigate }) {
  const [open, setOpen] = useState(false)

  if (item.children) {
    return (
      <div>
        <button
          onClick={() => setOpen(!open)}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
        >
          <item.icon size={18} className="flex-shrink-0" />
          {!collapsed && (
            <>
              <span className="flex-1 text-sm font-medium text-left">{item.label}</span>
              {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </>
          )}
        </button>
        {open && !collapsed && (
          <div className="ml-4 mt-1 space-y-1 border-l border-slate-700 pl-3">
            {item.children.map((child) => (
              <NavLink
                key={child.to}
                to={child.to}
                onClick={onNavigate}
                className={({ isActive }) =>
                  `flex items-center gap-2 px-2 py-2 rounded-lg text-sm transition-colors ${isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-400 hover:bg-slate-700 hover:text-white'
                  }`
                }
              >
                <child.icon size={15} />
                <span>{child.label}</span>
              </NavLink>
            ))}
          </div>
        )}
      </div>
    )
  }

  return (
    <NavLink
      to={item.to}
      onClick={onNavigate}
      className={({ isActive }) =>
        `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${isActive
          ? 'bg-blue-600 text-white'
          : 'text-slate-300 hover:bg-slate-700 hover:text-white'
        }`
      }
    >
      <item.icon size={18} className="flex-shrink-0" />
      {!collapsed && <span className="text-sm font-medium">{item.label}</span>}
    </NavLink>
  )
}

export default function Sidebar({ open, onClose }) {
  // On mobile: fixed overlay drawer; on desktop: inline collapsible
  return (
    <aside
      className={`
        bg-slate-800 flex-shrink-0 flex flex-col transition-all duration-300
        fixed inset-y-0 left-0 z-50
        md:relative md:inset-auto md:z-auto
        ${open ? 'translate-x-0 w-72 md:w-64' : '-translate-x-full md:translate-x-0 md:w-16'}
      `}
    >
      <div className="flex items-center gap-3 px-4 py-4 border-b border-slate-700">
        <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center flex-shrink-0">
          <Building2 size={16} className="text-white" />
        </div>
        {open && (
          <>
            <div className="flex-1 min-w-0">
              <h1 className="text-white font-bold text-sm leading-tight">Resolve.AI</h1>
              <p className="text-slate-400 text-xs">Facility Management</p>
            </div>
            {/* Close button visible on mobile only */}
            <button
              onClick={onClose}
              className="md:hidden p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700"
            >
              <X size={18} />
            </button>
          </>
        )}
      </div>
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {navItems.map((item, idx) => (
          <NavItem
            key={idx}
            item={item}
            collapsed={!open}
            onNavigate={onClose}
          />
        ))}
      </nav>
    </aside>
  )
}
