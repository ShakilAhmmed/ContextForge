export interface User {
  id: string;
  tenant_id: string;
  email: string;
  created_at: string;
}

export interface RegisterRequest {
  tenant_id: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenData {
  access_token: string;
  token_type: string;
  expires_in: number;
}
