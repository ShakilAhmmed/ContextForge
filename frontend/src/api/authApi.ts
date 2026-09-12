import { baseApi } from "./baseApi";
import type { LoginRequest, RegisterRequest, SuccessResponse, TokenData, User } from "./types";

export const authApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    register: builder.mutation<User, RegisterRequest>({
      query: (body) => ({ url: "/auth/register", method: "POST", body }),
      transformResponse: (response: SuccessResponse<User>) => response.data,
    }),

    login: builder.mutation<TokenData, LoginRequest>({
      query: (body) => ({ url: "/auth/login", method: "POST", body }),
      transformResponse: (response: SuccessResponse<TokenData>) => response.data,
    }),

    logout: builder.mutation<void, void>({
      query: () => ({ url: "/auth/logout", method: "POST" }),
    }),

    getMe: builder.query<User, void>({
      query: () => "/auth/me",
      transformResponse: (response: SuccessResponse<User>) => response.data,
    }),
  }),
  overrideExisting: false,
});

export const { useRegisterMutation, useLoginMutation, useLogoutMutation, useGetMeQuery } = authApi;
