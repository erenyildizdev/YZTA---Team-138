import type { ReactNode } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation, useNavigate } from "react-router";
import { AppLayout } from "./components/layout/AppLayout";
import { AnalysisPage } from "./pages/AnalysisPage";
import { DashboardPage } from "./pages/DashboardPage";
import { HistoryPage } from "./pages/HistoryPage";
import { LoadingPage } from "./pages/LoadingPage";
import { LoginPage } from "./pages/LoginPage";
import { MentorPage } from "./pages/MentorPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ReportPage } from "./pages/ReportPage";
import { AuthProvider, useAuth } from "./context/AuthContext";

function RequireAuth({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <>{children}</>;
}

function AppRoutes() {
  const navigate = useNavigate();

  return (
    <Routes>
      <Route path="login" element={<LoginPage />} />
      <Route path="register" element={<RegisterPage />} />
      <Route
        element={
          <RequireAuth>
            <AppLayout />
          </RequireAuth>
        }
      >
        <Route
          index
          element={
            <DashboardPage
              onNew={() => navigate("/mentor")}
              onViewAll={() => navigate("/history")}
              onOpenDetail={() => navigate("/analysis")}
            />
          }
        />
        <Route path="mentor" element={<MentorPage onAnalyze={() => navigate("/analysis/loading")} />} />
        <Route path="analysis/loading" element={<LoadingPage onDone={() => navigate("/analysis")} />} />
        <Route path="analysis" element={<AnalysisPage onReport={() => navigate("/report")} />} />
        <Route path="report" element={<ReportPage onBack={() => navigate("/analysis")} />} />
        <Route path="history" element={<HistoryPage onOpen={() => navigate("/analysis")} />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}
