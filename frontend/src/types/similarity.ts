export interface SectionSimilarityScore {
  section_id: string;
  section_title: string;
  similarity_percent: number;
  word_count: number;
  flagged_count: number;
}

export interface FlaggedSimilarityFragment {
  id: string;
  section_title: string;
  text: string;
  category: 'boilerplate' | 'literature_overlap' | 'self_repetition' | 'unquoted_overlap';
  matched_source: string;
  similarity_degree: number;
  explanation: string;
  recommendation: string;
  suggested_rewrite?: string;
}

export interface SimilarityCategories {
  boilerplate_percent: number;
  literature_overlap_percent: number;
  direct_unquoted_percent: number;
}

export interface SimilarityFilters {
  exclude_references: boolean;
  exclude_quotes: boolean;
  min_words_threshold: number;
}

export interface SimilarityAuditReport {
  overall_similarity_percent: number;
  originality_percent: number;
  risk_level: 'low' | 'moderate' | 'high';
  risk_label: string;
  total_words_analyzed: number;
  categories: SimilarityCategories;
  section_scores: SectionSimilarityScore[];
  flagged_fragments: FlaggedSimilarityFragment[];
  filters_applied: SimilarityFilters;
}
