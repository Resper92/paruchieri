export interface Salon {
  id: number;
  owner_id: number;
  name: string;
  address: string | null;
}

export interface SalonCreate {
  owner_id: number;
  name: string;
  address?: string | null;
}
