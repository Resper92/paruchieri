export interface Appointment {
  id: number;
  client_id: number;
  staff_id: number;
  service_id: number;
  start_time: string;
  end_time: string;
  status: string;
}

export interface AppointmentCreate {
  staff_id: number;
  service_id: number;
  start_time: string;
  end_time: string;
  status?: string;
}
