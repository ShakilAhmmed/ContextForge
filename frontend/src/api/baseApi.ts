import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export const baseApi = createApi({
  reducerPath: "api",
  baseQuery: fetchBaseQuery({
    baseUrl: API_BASE_URL,
    // Auth is an httpOnly cookie now, not a token in Redux/localStorage -
    // the browser attaches it automatically, but only if we ask it to send
    // cookies cross-origin at all.
    credentials: "include",
    prepareHeaders: (headers) => {
      // CSRF defense for the backend's cookie-authenticated requests: a
      // plain cross-site form can't set custom headers, and a cross-site
      // fetch attempt gets blocked by CORS before this header would even
      // matter (see app/api/deps.py on the backend for the full reasoning).
      // The value doesn't need to be a secret - only its presence matters.
      headers.set("X-CSRF-Token", "1");
      return headers;
    },
  }),
  tagTypes: ["Document"],
  endpoints: () => ({}),
});
