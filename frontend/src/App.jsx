import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import PrivateRoute from './components/PrivateRoute'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import BuildingsList from './pages/buildings/BuildingsList'
import FloorsList from './pages/buildings/FloorsList'
import UnitsList from './pages/buildings/UnitsList'
import UsersList from './pages/users/UsersList'
import VendorsList from './pages/vendors/VendorsList'
import CleaningScheduleList from './pages/cleaning/CleaningScheduleList'
import PreventiveList from './pages/maintenance/PreventiveList'
import CorrectiveList from './pages/maintenance/CorrectiveList'
import CasesList from './pages/cases/CasesList'
import CostsList from './pages/costs/CostsList'
import RosterList from './pages/roster/RosterList'
import AttendancePage from './pages/attendance/AttendancePage'
import Analytics from './pages/analytics/Analytics'
import ClientsList from './pages/clients/ClientsList'
import ContractsList from './pages/contracts/ContractsList'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/*"
          element={
            <PrivateRoute>
              <Layout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/buildings" element={<BuildingsList />} />
                  <Route path="/floors" element={<FloorsList />} />
                  <Route path="/units" element={<UnitsList />} />
                  <Route path="/users" element={<UsersList />} />
                  <Route path="/vendors" element={<VendorsList />} />
                  <Route path="/cleaning" element={<CleaningScheduleList />} />
                  <Route path="/maintenance/preventive" element={<PreventiveList />} />
                  <Route path="/maintenance/corrective" element={<CorrectiveList />} />
                  <Route path="/cases" element={<CasesList />} />
                  <Route path="/costs" element={<CostsList />} />
                  <Route path="/roster" element={<RosterList />} />
                  <Route path="/attendance/cleaner" element={<AttendancePage attendanceType="cleaner" />} />
                  <Route path="/attendance/security" element={<AttendancePage attendanceType="security" />} />
                  <Route path="/analytics" element={<Analytics />} />
                  <Route path="/clients" element={<ClientsList />} />
                  <Route path="/contracts" element={<ContractsList />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Layout>
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App
