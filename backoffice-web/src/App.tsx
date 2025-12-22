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
import EditPalettePage from './pages/palettes/EditPalettePage';
// Expeditions removed - replaced by Bons d'Enlèvement and Bons de Réception Retour
import RFIDTagsListPage from './pages/rfidTags/RFIDTagsListPage';
import UsersListPage from './pages/users/UsersListPage';
import NotificationsPage from './pages/notifications/NotificationsPage';
import ReportsPage from './pages/reports/ReportsPage';
import PartnersListPage from './pages/partners/PartnersListPage';
import CreatePartnerPage from './pages/partners/CreatePartnerPage';
import EditPartnerPage from './pages/partners/EditPartnerPage';
import PartnerDetailsPage from './pages/partners/PartnerDetailsPage';
import ContactsListPage from './pages/contacts/ContactsListPage';
import CreateContactPage from './pages/contacts/CreateContactPage';
import EditContactPage from './pages/contacts/EditContactPage';
import ContactDetailsPage from './pages/contacts/ContactDetailsPage';
import DistributeursListPage from './pages/distributeurs/DistributeursListPage';
import DistributeurDetailsPage from './pages/distributeurs/DistributeurDetailsPage';
import CreateDistributeurPage from './pages/distributeurs/CreateDistributeurPage';
import EditDistributeurPage from './pages/distributeurs/EditDistributeurPage';
import GroupesListPage from './pages/groupes/GroupesListPage';
import GroupeDetailsPage from './pages/groupes/GroupeDetailsPage';
import CreateGroupePage from './pages/groupes/CreateGroupePage';
import EditGroupePage from './pages/groupes/EditGroupePage';
import CentresRemplisseursListPage from './pages/centresRemplisseurs/CentresRemplisseursListPage';
import CentreRemplisseurDetailsPage from './pages/centresRemplisseurs/CentreRemplisseurDetailsPage';
import CreateCentreRemplisseurPage from './pages/centresRemplisseurs/CreateCentreRemplisseurPage';
import EditCentreRemplisseurPage from './pages/centresRemplisseurs/EditCentreRemplisseurPage';
import DepotsListPage from './pages/depots/DepotsListPage';
import DepotDetailsPage from './pages/depots/DepotDetailsPage';
import CreateDepotPage from './pages/depots/CreateDepotPage';
import BonsEnlevementHomePage from './pages/bonsEnlevement/BonsEnlevementHomePage';
import BonsEnlevementListPage from './pages/bonsEnlevement/BonsEnlevementListPage';
import BonEnlevementDetailsPage from './pages/bonsEnlevement/BonEnlevementDetailsPage';
import CreateBonEnlevementPage from './pages/bonsEnlevement/CreateBonEnlevementPage';
import EditBonEnlevementPage from './pages/bonsEnlevement/EditBonEnlevementPage';
import BonsReceptionRetourHomePage from './pages/bonsReceptionRetour/BonsReceptionRetourHomePage';
import BonsReceptionRetourListPage from './pages/bonsReceptionRetour/BonsReceptionRetourListPage';
import BonReceptionRetourDetailsPage from './pages/bonsReceptionRetour/BonReceptionRetourDetailsPage';
import CreateBonReceptionRetourPage from './pages/bonsReceptionRetour/CreateBonReceptionRetourPage';
import NotFoundPage from './pages/NotFoundPage';
import ProfilePage from './pages/profile/ProfilePage';
import SettingsPage from './pages/settings/SettingsPage';
import ThemeSettingsPage from './pages/settings/ThemeSettingsPage';

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
            <Route path="palettes/:id/edit" element={<EditPalettePage />} />

            {/* RFID Tags */}
            <Route path="rfid-tags" element={<RFIDTagsListPage />} />

            {/* Users (Admin only) */}
            <Route path="users" element={<UsersListPage />} />

            {/* Notifications */}
            <Route path="notifications" element={<NotificationsPage />} />

            {/* Reports */}
            <Route path="reports" element={<ReportsPage />} />

            {/* Partners */}
            <Route path="partners" element={<PartnersListPage />} />
            <Route path="partners/new" element={<CreatePartnerPage />} />
            <Route path="partners/:id" element={<PartnerDetailsPage />} />
            <Route path="partners/:id/edit" element={<EditPartnerPage />} />

            {/* Contacts */}
            <Route path="contacts" element={<ContactsListPage />} />
            <Route path="contacts/new" element={<CreateContactPage />} />
            <Route path="contacts/:id" element={<ContactDetailsPage />} />
            <Route path="contacts/:id/edit" element={<EditContactPage />} />

            {/* Distributeurs */}
            <Route path="distributeurs" element={<DistributeursListPage />} />
            <Route path="distributeurs/new" element={<CreateDistributeurPage />} />
            <Route path="distributeurs/:id" element={<DistributeurDetailsPage />} />
            <Route path="distributeurs/:id/edit" element={<EditDistributeurPage />} />

            {/* Groupes */}
            <Route path="groupes" element={<GroupesListPage />} />
            <Route path="groupes/new" element={<CreateGroupePage />} />
            <Route path="groupes/:id" element={<GroupeDetailsPage />} />
            <Route path="groupes/:id/edit" element={<EditGroupePage />} />

            {/* Centres Remplisseurs */}
            <Route path="centres-remplisseurs" element={<CentresRemplisseursListPage />} />
            <Route path="centres-remplisseurs/new" element={<CreateCentreRemplisseurPage />} />
            <Route path="centres-remplisseurs/:id" element={<CentreRemplisseurDetailsPage />} />
            <Route path="centres-remplisseurs/:id/edit" element={<EditCentreRemplisseurPage />} />

            {/* Dépôts */}
            <Route path="depots" element={<DepotsListPage />} />
            <Route path="depots/new" element={<CreateDepotPage />} />
            <Route path="depots/:id" element={<DepotDetailsPage />} />

            {/* Bons d'Enlèvement */}
            <Route path="bons-enlevement" element={<BonsEnlevementHomePage />} />
            <Route path="bons-enlevement/list" element={<BonsEnlevementListPage />} />
            <Route path="bons-enlevement/new" element={<CreateBonEnlevementPage />} />
            <Route path="bons-enlevement/:id" element={<BonEnlevementDetailsPage />} />
            <Route path="bons-enlevement/:id/edit" element={<EditBonEnlevementPage />} />

            {/* Bons de Réception Retour */}
            <Route path="bons-reception-retour" element={<BonsReceptionRetourHomePage />} />
            <Route path="bons-reception-retour/list" element={<BonsReceptionRetourListPage />} />
            <Route path="bons-reception-retour/new" element={<CreateBonReceptionRetourPage />} />
            <Route path="bons-reception-retour/:id" element={<BonReceptionRetourDetailsPage />} />

            {/* Profile & Settings */}
            <Route path="profile" element={<ProfilePage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="settings/theme" element={<ThemeSettingsPage />} />
          </Route>

          {/* 404 */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
