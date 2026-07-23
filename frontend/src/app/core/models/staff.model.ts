export interface Staff {
  id: number;
  salon_id: number;
  name: string;
}

export interface StaffCreate {
  salon_id: number;
  name: string;
}
