export interface LoginRequest {
  username: string;
  password: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserResponse {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  is_verified: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}
