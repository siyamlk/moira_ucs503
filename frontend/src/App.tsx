import { Navigate, Route, Routes } from "react-router-dom";

import { ProtectedRoute } from "./components/common/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";
import { AppLayout } from "./layouts/AppLayout";
import { BacklogsPage } from "./pages/backlogs/BacklogsPage";
import { LoginPage } from "./pages/auth/LoginPage";
import { SignupPage } from "./pages/auth/SignupPage";
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

        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  );
}
