import { Navigate, Route, Routes } from "react-router-dom";

import { AdminRoute } from "./components/common/AdminRoute";
import { ProtectedRoute } from "./components/common/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";
import { AdminLayout } from "./layouts/AdminLayout";
import { AppLayout } from "./layouts/AppLayout";
import { BacklogsPage } from "./pages/backlogs/BacklogsPage";
import { LoginPage } from "./pages/auth/LoginPage";
import { SignupPage } from "./pages/auth/SignupPage";
import { AdminBookingsPage } from "./pages/admin/AdminBookingsPage";
import { AdminConfigPage } from "./pages/admin/AdminConfigPage";
import { AdminDashboardPage } from "./pages/admin/AdminDashboardPage";
import { AdminElectivesPage } from "./pages/admin/AdminElectivesPage";
import { AdminFacultyPage } from "./pages/admin/AdminFacultyPage";
import { AdminSchedulesPage } from "./pages/admin/AdminSchedulesPage";
import { DashboardPage } from "./pages/dashboard/DashboardPage";
import { ElectivesPage } from "./pages/electives/ElectivesPage";
import { FacultyPage } from "./pages/faculty/FacultyPage";
import { ProfilePage } from "./pages/profile/ProfilePage";
import { RecommendationsPage } from "./pages/recommendations/RecommendationsPage";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />

        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/recommendations" element={<RecommendationsPage />} />
          <Route path="/electives" element={<ElectivesPage />} />
          <Route path="/backlogs" element={<BacklogsPage />} />
          <Route path="/faculty" element={<FacultyPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Route>

        <Route
          element={
            <AdminRoute>
              <AdminLayout />
            </AdminRoute>
          }
        >
          <Route path="/admin" element={<AdminDashboardPage />} />
          <Route path="/admin/electives" element={<AdminElectivesPage />} />
          <Route path="/admin/faculty" element={<AdminFacultyPage />} />
          <Route path="/admin/schedules" element={<AdminSchedulesPage />} />
          <Route path="/admin/bookings" element={<AdminBookingsPage />} />
          <Route path="/admin/config" element={<AdminConfigPage />} />
        </Route>

        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  );
}
