import { baseApi } from "./baseApi";
import type { CreateTenantRequest, SuccessResponse, Tenant } from "./types";

export const tenantApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    createTenant: builder.mutation<Tenant, CreateTenantRequest>({
      query: (body) => ({ url: "/tenants", method: "POST", body }),
      transformResponse: (response: SuccessResponse<Tenant>) => response.data,
    }),
  }),
  overrideExisting: false,
});

export const { useCreateTenantMutation } = tenantApi;
