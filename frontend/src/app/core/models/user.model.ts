export enum Role {
  Superadmin = 'superadmin',
  Parrucchiere = 'parrucchiere',
  Client = 'client',
}

export interface User {
  id: number;
  email: string;
  role: Role;
}

export interface RegisterRequest {
  email: string;
  password: string;
  role: Role;
}
