export type FeedCalculatorSeason = 'winter' | 'spring_buildup' | 'summer_gap';
export type FeedCalculatorColonyStrength = 'weak' | 'medium' | 'strong';

export interface FeedCalculatorRequest {
  colony_count: number;
  colony_strength: FeedCalculatorColonyStrength;
  season: FeedCalculatorSeason;
}

export interface FeedCalculatorResponse {
  kg_sugar_per_colony: number;
  total_kg_sugar: number;
  formula_note: string;
}

export interface HoneyPriceCalculatorRequest {
  apiary_id: number;
  from_date?: string;
  to_date?: string;
  target_margin_percent: number;
}

export interface HoneyPriceCalculatorResponse {
  apiary_id: number;
  total_relevant_costs: number;
  total_harvested_kg: number;
  colony_count: number;
  cost_per_kg: number | null;
  cost_per_colony: number | null;
  suggested_price_per_kg: number | null;
  simplification_note: string;
}
