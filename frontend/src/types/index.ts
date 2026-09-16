export interface User {
  id: number;
  full_name: string;
  student_id: string;
  email: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Profile {
  id: number;
  semester: number;
  branch: string;
  cgpa: number;
  credits_earned: number;
  credits_required: number;
  career_goal: string;
  interests: string[];
  raw_intent_text: string;
  skills: string[];
  completed_courses: string[];
  preferred_domains: string[];
  career_preference: string;
  current_basket: string;
}

export interface ProfileUpdatePayload {
  semester?: number;
  branch?: string;
  cgpa?: number;
  credits_earned?: number;
  credits_required?: number;
  career_goal?: string;
  interests?: string[];
  raw_intent_text?: string;
  skills?: string[];
  completed_courses?: string[];
  preferred_domains?: string[];
  career_preference?: string;
  current_basket?: string;
}

export interface FacultySchedule {
  id: number;
  day: string;
  start_time: string;
  end_time: string;
  room: string;
  note: string;
}

export interface Faculty {
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
  schedules: FacultySchedule[];
}

export interface Elective {
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
  faculty: Faculty | null;
}

export interface RecommendRequestPayload {
  free_text: string;
  interests: string[];
  career_goal: string;
}

// The exact arithmetic behind match_percent — these four *_points fields
// always sum to it (see backend/app/services/recommendation_service.py).
export interface ScoreBreakdown {
  interest_points: number;
  interest_matched: number;
  interest_total: number;
  career_points: number;
  career_matched: boolean;
  topic_points: number;
  topic_matched: number;
  topic_total: number;
  bonus_points: number;
}

export interface Recommendation {
  elective: Elective;
  match_percent: number;
  interest_match: boolean;
  career_match: boolean;
  matched_topics: string[];
  explanation: string;
  score_breakdown: ScoreBreakdown;
  suggested_faculty: Faculty[];
}

export interface RecommendResponse {
  interpreted_tags: string[];
  career_goal: string;
  top_recommendation: Recommendation | null;
  alternatives: Recommendation[];
}

export interface Backlog {
  id: number;
  subject: string;
  course_code: string;
  credits: number;
  course_type: string;
  current_grade: string;
  status: string;
  created_at: string;
}

export interface BacklogCreatePayload {
  subject: string;
  course_code: string;
  credits: number;
  course_type: string;
  current_grade: string;
}

export interface PrioritizedBacklog {
  backlog: Backlog;
  priority_rank: number;
  priority_label: "CRITICAL" | "HIGH" | "MODERATE";
  cgpa_impact: number;
  estimated_new_cgpa: number;
  explanation: string;
}

export interface PrioritizeResponse {
  current_cgpa: number;
  pending_count: number;
  prioritized: PrioritizedBacklog[];
}
