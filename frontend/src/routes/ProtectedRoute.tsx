import { useEffect } from "react";
import type { ReactElement } from "react";
import { Navigate } from "react-router-dom";

import { useGetMeQuery } from "../api/authApi";
import { useAppDispatch } from "../app/hooks";
import { LoadingScreen } from "../components/LoadingScreen";
import { userSet } from "../features/auth/authSlice";

export function ProtectedRoute({ children }: { children: ReactElement }): ReactElement {
  // Cookie is httpOnly - JS can't check it directly. "Logged in" is
  // whatever this call says, not client-side state.
  const { data, isLoading, isError } = useGetMeQuery();
  const dispatch = useAppDispatch();

  useEffect(() => {
    if (data) dispatch(userSet(data));
  }, [data, dispatch]);

  if (isLoading) return <LoadingScreen />;

  if (isError || !data) return <Navigate to="/login" replace />;

  return children;
}
