import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

import type { User } from "../../api/types";

interface AuthState {
  user: User | null;
}

// No token here at all - it lives only in the httpOnly cookie the browser
// manages, invisible to this (or any) JS. "Am I logged in" is answered by
// GET /auth/me succeeding (see ProtectedRoute), not by client-side state.
// `user` is just a display cache, populated from that same call.
const initialState: AuthState = { user: null };

// Cleanup for browsers that persisted auth data under an earlier build
// (first localStorage, briefly; now cookie-based) - dead key, never read.
try {
  localStorage.removeItem("contextforge.auth");
} catch {
  // storage unavailable - nothing to clean up
}

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    userSet(state, action: PayloadAction<User>) {
      state.user = action.payload;
    },
    loggedOut(state) {
      state.user = null;
    },
  },
});

export const { userSet, loggedOut } = authSlice.actions;
export const authReducer = authSlice.reducer;
