import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './theme/ThemeProvider';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import { DashboardLayout } from './components/layout/DashboardLayout';

// Pages
import LoginPage from './pages/auth/LoginPage';
import DashboardPage from './pages/dashboard/DashboardPage';
import PalettesListPage from './pages/palettes/PalettesListPage';
import PaletteDetailsPage from './pages/palettes/PaletteDetailsPage';
import CreatePalettePage from './pages/palettes/CreatePalettePage';
import ExpeditionsListPage from './pages/expeditions/ExpeditionsListPage';
import ExpeditionDetailsPage from './pages/expeditions/ExpeditionDetailsPage';
import CreateExpeditionPage from './pages/expeditions/CreateExpeditionPage';
import UsersListPage from './pages/users/UsersListPage';
import NotificationsPage from './pages/notifications/NotificationsPage';
import ReportsPage from './pages/reports/ReportsPage';
import NotFoundPage from './pages/NotFoundPage';

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />

          {/* Protected routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />

            {/* Palettes */}
            <Route path="palettes" element={<PalettesListPage />} />
            <Route path="palettes/new" element={<CreatePalettePage />} />
            <Route path="palettes/:id" element={<PaletteDetailsPage />} />

            {/* Expeditions */}
            <Route path="expeditions" element={<ExpeditionsListPage />} />
            <Route path="expeditions/new" element={<CreateExpeditionPage />} />
            <Route path="expeditions/:id" element={<ExpeditionDetailsPage />} />

            {/* Users (Admin only) */}
            <Route path="users" element={<UsersListPage />} />

            {/* Notifications */}
            <Route path="notifications" element={<NotificationsPage />} />

            {/* Reports */}
            <Route path="reports" element={<ReportsPage />} />
          </Route>

          {/* 404 */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
