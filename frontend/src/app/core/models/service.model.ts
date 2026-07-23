export interface Service {
  id: number;
  salon_id: number;
  name: string;
  price: number | null;
  duration_minutes: number | null;
}

export interface ServiceCreate {
  salon_id: number;
  name: string;
  price?: number | null;
  duration_minutes?: number | null;
}
