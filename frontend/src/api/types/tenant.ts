export interface Tenant {
  id: string;
  name: string;
  slug: string;
  created_at: string;
}

export interface CreateTenantRequest {
  name: string;
  slug: string;
}
