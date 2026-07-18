import { BrowserRouter, Navigate, Route, Routes, useNavigate } from "react-router";
import { AppLayout } from "./components/layout/AppLayout";
import { AnalysisPage } from "./pages/AnalysisPage";
import { DashboardPage } from "./pages/DashboardPage";
import { HistoryPage } from "./pages/HistoryPage";
import { LoadingPage } from "./pages/LoadingPage";
import { MentorPage } from "./pages/MentorPage";
import { ReportPage } from "./pages/ReportPage";

function AppRoutes() {
  const navigate = useNavigate();

  return (
    <Routes>
      <Route element={<AppLayout />}>
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
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}
