import type { FacultySchedule } from "./index";

export interface AdminSchedule {
  id: number;
  faculty_id: number;
  day: string;
  start_time: string;
  end_time: string;
  room: string;
  note: string;
  semester: string;
}

export interface AdminScheduleInput {
  faculty_id: number;
  day: string;
  start_time: string;
  end_time: string;
  room?: string;
  note?: string;
  semester?: string;
}

export interface AdminFaculty {
  id: number;
  ref_code: string;
  name: string;
  title: string;
  department: string;
  specialization: string;
  research_interests: string[];
  office_location: string;
  email: string;
  photo_url: string;
  profile_url: string;
  schedules: AdminSchedule[];
}

export interface AdminFacultyInput {
  ref_code: string;
  name: string;
  title?: string;
  department?: string;
  specialization?: string;
  research_interests?: string[];
  office_location?: string;
  email?: string;
  photo_url?: string;
  profile_url?: string;
}

export interface AdminElective {
  id: number;
  code: string;
  title: string;
  department: string;
  credits: number;
  prerequisites: string;
  description: string;
  category: string;
  basket: string;
  topics: string[];
  syllabus_outline: string[];
  interest_tags: string[];
  career_tags: string[];
  faculty_id: number | null;
}

export interface AdminElectiveInput {
  code: string;
  title: string;
  department?: string;
  credits?: number;
  prerequisites?: string;
  description?: string;
  category?: string;
  basket?: string;
  topics?: string[];
  syllabus_outline?: string[];
  interest_tags?: string[];
  career_tags?: string[];
  faculty_id?: number | null;
}

export interface AuditLogEntry {
  id: number;
  admin_id: number | null;
  action: string;
  entity_type: string;
  entity_id: number | null;
  details: Record<string, unknown> | null;
  created_at: string;
}

export interface DashboardStats {
  total_electives: number;
  total_faculty: number;
  total_baskets: number;
  total_categories: number;
  total_active_bookings: number;
  recent_activity: AuditLogEntry[];
}

export interface AcademicConfig {
  id: number;
  key: string;
  value: unknown;
  description: string;
  updated_at: string;
  updated_by: number | null;
}

export interface AcademicConfigUpdatePayload {
  value: unknown;
  description?: string;
}

export interface AdminBooking {
  id: number;
  student_id: number;
  student_name: string;
  student_email: string;
  faculty_id: number;
  faculty_name: string;
  // The backend nests a plain ScheduleOut here (id/day/start_time/end_time/
  // room/note/is_booked), not the full AdminSchedule shape — it has no
  // faculty_id/semester of its own since those already live one level up.
  schedule: FacultySchedule;
  status: string;
  created_at: string;
}

export interface RecommendationWeights {
  interest: number;
  career: number;
  syllabus: number;
  skill: number;
  academic: number;
  prerequisite: number;
}
