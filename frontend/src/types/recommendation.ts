import type { Elective } from "./index";

export interface StudentProfileInput {
  program?: string;
  semester?: number;
  interests?: string[];
  career_goals?: string[];
  skills?: string[];
  completed_courses?: string[];
  preferred_domains?: string[];
  career_preference?: string;
  free_text?: string;
  current_basket?: string;
}

export interface RecommendationRequestPayload {
  student_profile?: StudentProfileInput;
  elective_slot?: string | null;
}

export interface MatchComponent {
  key: string;
  label: string;
  earned: number;
  max: number;
}

export interface MatchBreakdown {
  components: MatchComponent[];
  total: number;
  max_total: number;
}

export interface PrerequisiteCheck {
  name: string;
  satisfied: boolean;
}

export interface RecommendationItem {
  course_code: string;
  course_name: string;
  elective: Elective;
  match_percentage: number;
  score_breakdown: MatchBreakdown;
  matched_interests: string[];
  matched_career_goals: string[];
  matched_skills: string[];
  matched_syllabus_topics: string[];
  prerequisite_checks: PrerequisiteCheck[];
  why_this_matches: string;
  career_relevance: string;
  syllabus_alignment: string;
  skill_alignment: string;
  academic_context: string;
  prerequisite_context: string;
  explanation: string;
}

export interface AllEligibleItem extends RecommendationItem {
  domain: string;
  short_reason: string;
}

export interface BasketRecommendation {
  basket_name: string;
  match_percentage: number;
  electives: RecommendationItem[];
  matched_interests: string[];
  matched_career_goals: string[];
  why_this_basket_matches: string;
}

export interface RecommendationApiResponse {
  interpreted_interests: string[];
  interpreted_career_goals: string[];
  elective_slot: string | null;
  current_basket: string | null;
  available_baskets: string[];
  primary_basket: BasketRecommendation | null;
  alternative_baskets: BasketRecommendation[];
  all_baskets: BasketRecommendation[];
  primary_recommendation: RecommendationItem | null;
  alternatives: RecommendationItem[];
  all_eligible_courses: AllEligibleItem[];
  weights: Record<string, number>;
  branch_warning: string | null;
}
