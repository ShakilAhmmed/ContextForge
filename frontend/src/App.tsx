import { Navigate, Route, Routes } from "react-router-dom";

import { CreateTenantPage } from "./features/tenants/CreateTenantPage";
import { LoginPage } from "./features/auth/LoginPage";
import { RegisterPage } from "./features/auth/RegisterPage";
import { ChatPage } from "./features/chat/ChatPage";
import { DocumentDetailPage } from "./features/documents/DocumentDetailPage";
import { DocumentsPage } from "./features/documents/DocumentsPage";
import { ProtectedRoute } from "./routes/ProtectedRoute";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/documents" replace />} />
      <Route path="/create-tenant" element={<CreateTenantPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/documents"
        element={
          <ProtectedRoute>
            <DocumentsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/documents/:id"
        element={
          <ProtectedRoute>
            <DocumentDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/chat"
        element={
          <ProtectedRoute>
            <ChatPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/documents" replace />} />
    </Routes>
  );
}
