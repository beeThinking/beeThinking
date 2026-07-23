export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';
export type TaskStatus = 'open' | 'done' | 'cancelled';
export type TaskSource = 'manual' | 'inspection' | 'system';
export type TaskKind = 'todo' | 'appointment';
export type VarroaTreatmentType =
  | 'formic_acid_short'
  | 'formic_acid_long'
  | 'thymol'
  | 'oxalic_acid_dribble'
  | 'oxalic_acid_sublimation'
  | 'lactic_acid'
  | 'biotechnical'
  | 'other';
export type VarroaWeatherRating = 'suitable' | 'caution' | 'unsuitable' | 'unknown';

export interface VarroaWeatherWindow {
  id: number;
  apiary_id: number;
  source: string;
  provider_version: string;
  treatment_type: VarroaTreatmentType;
  date: string;
  rating: VarroaWeatherRating;
  reason: string;
  min_temperature: number | null;
  max_temperature: number | null;
  avg_humidity: number | null;
  precipitation_probability: number | null;
  wind_speed: number | null;
  fetched_at: string;
  created_at: string | null;
}

export interface VarroaAssistant {
  hive_id: number;
  apiary_id: number;
  source_note: string;
  windows: VarroaWeatherWindow[];
}

export interface Photo {
  id: number;
  owner_id: number;
  hive_id: number | null;
  inspection_id: number | null;
  object_key: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  caption: string | null;
  created_at: string;
}

export interface PhotoPreview {
  url: string;
}

export interface PhotoWithPreview extends Photo {
  preview_url: string | null;
}

export interface Task {
  id: number;
  owner_id: number;
  hive_id: number | null;
  apiary_id: number | null;
  title: string;
  description: string | null;
  due_date: string | null;
  start_at: string | null;
  end_at: string | null;
  kind: TaskKind;
  priority: TaskPriority;
  status: TaskStatus;
  source: TaskSource;
  created_at: string;
  updated_at: string | null;
  completed_at: string | null;
}

export interface TaskCreate {
  hive_id?: number | null;
  apiary_id?: number | null;
  title: string;
  description?: string;
  due_date?: string;
  start_at?: string;
  end_at?: string;
  kind?: TaskKind;
  priority?: TaskPriority;
  status?: TaskStatus;
  source?: TaskSource;
}

export type TaskUpdate = Partial<Omit<TaskCreate, 'description' | 'due_date' | 'start_at' | 'end_at'>> & {
  description?: string | null;
  due_date?: string | null;
  start_at?: string | null;
  end_at?: string | null;
};

export interface Treatment {
  id: number;
  owner_id: number;
  hive_id: number;
  started_at: string;
  ended_at: string | null;
  product: string;
  method: string | null;
  dosage: string | null;
  reason: string | null;
  notes: string | null;
  weather_window_id: number | null;
  weather_rating: string | null;
  weather_source: string | null;
  weather_fetched_at: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface TreatmentCreate {
  hive_id: number;
  started_at: string;
  ended_at?: string;
  product: string;
  method?: string;
  dosage?: string;
  reason?: string;
  notes?: string;
  weather_window_id?: number | null;
}

export type TreatmentUpdate = Partial<TreatmentCreate>;

export interface Harvest {
  id: number;
  owner_id: number;
  apiary_id: number | null;
  hive_id: number | null;
  harvest_date: string;
  crop_type: string | null;
  amount_kg: number;
  water_content_percent: number | null;
  batch_code: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface HarvestCreate {
  apiary_id?: number | null;
  hive_id?: number | null;
  harvest_date: string;
  crop_type?: string;
  amount_kg: number;
  water_content_percent?: number | null;
  batch_code?: string;
  notes?: string;
}

export type HarvestUpdate = Partial<HarvestCreate>;

export interface Feeding {
  id: number;
  owner_id: number;
  apiary_id: number | null;
  hive_id: number | null;
  date: string;
  feed_type: string;
  amount_kg_or_l: number;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface FeedingCreate {
  apiary_id?: number | null;
  hive_id?: number | null;
  date: string;
  feed_type: string;
  amount_kg_or_l: number;
  notes?: string;
}

export type FeedingUpdate = Partial<FeedingCreate>;

export type ArticleCategory = 'honey' | 'material' | 'feed' | 'other';

export interface Article {
  id: number;
  owner_id: number;
  category: ArticleCategory;
  name: string;
  sku: string | null;
  weight_kg: number | null;
  unit: string;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface ArticleCreate {
  category?: ArticleCategory;
  name: string;
  sku?: string;
  weight_kg?: number | null;
  unit?: string;
  notes?: string;
}

export type ArticleUpdate = Partial<ArticleCreate>;

export interface InventoryItem {
  id: number;
  owner_id: number;
  article_id: number;
  article: Article;
  quantity: number;
  unit: string;
  price: number | null;
  best_before: string | null;
  batch_code: string | null;
  archived: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface InventoryItemCreate {
  article_id: number;
  quantity?: number;
  unit?: string;
  price?: number | null;
  best_before?: string | null;
  batch_code?: string;
  archived?: boolean;
  notes?: string;
}

export type InventoryItemUpdate = Partial<InventoryItemCreate>;

export interface DashboardHiveStatus {
  hive_id: number;
  name: string;
  status: string;
  swarm_risk: string;
  latest_inspection_date: string | null;
}

export type CashbookDirection = 'income' | 'expense';

export interface CashbookEntry {
  id: number;
  apiary_id: number | null;
  owner_id: number;
  performed_by_user_id: number;
  booking_date: string;
  direction: CashbookDirection;
  category: string;
  title: string | null;
  invoice_number: string | null;
  partner_id: number | null;
  amount_gross: number;
  tax_rate: number;
  tax_amount: number;
  amount_net: number;
  counterparty: string | null;
  description: string | null;
  payment_method: string | null;
  receipt_id: number | null;
  created_at: string;
  updated_at: string | null;
}

export interface CashbookEntryCreate {
  apiary_id?: number | null;
  booking_date: string;
  direction: CashbookDirection;
  category: string;
  title?: string;
  invoice_number?: string;
  partner_id?: number | null;
  amount_gross: number;
  tax_rate?: number;
  tax_amount?: number;
  amount_net: number;
  counterparty?: string;
  description?: string;
  payment_method?: string;
  receipt_id?: number | null;
}

export type CashbookEntryUpdate = Partial<CashbookEntryCreate>;

export interface CashbookSummary {
  income: number;
  expenses: number;
  surplus: number;
}

export type OfficePartnerType = 'customer' | 'supplier';
export type OfficeDocumentType = 'receipt' | 'invoice' | 'offer' | 'report';
export type OfficeDocumentStatus = 'draft' | 'sent' | 'accepted' | 'paid' | 'cancelled';

export interface OfficePartner {
  id: number;
  owner_id: number;
  partner_type: OfficePartnerType;
  name: string;
  email: string | null;
  phone: string | null;
  address: string | null;
  tax_id: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface OfficePartnerCreate {
  partner_type: OfficePartnerType;
  name: string;
  email?: string;
  phone?: string;
  address?: string;
  tax_id?: string;
  notes?: string;
}

export type OfficePartnerUpdate = Partial<OfficePartnerCreate>;

export interface OfficeLineItem {
  description: string;
  quantity: number;
  unit_price: number;
  tax_rate: number;
}

export interface OfficeDocument {
  id: number;
  owner_id: number;
  partner_id: number | null;
  document_type: OfficeDocumentType;
  status: OfficeDocumentStatus;
  document_number: string;
  title: string;
  document_date: string;
  due_date: string | null;
  amount_gross: number;
  tax_rate: number;
  tax_amount: number;
  amount_net: number;
  line_items: OfficeLineItem[];
  notes: string | null;
  receipt_id: number | null;
  cashbook_entry_id: number | null;
  created_at: string;
  updated_at: string | null;
}

export interface OfficeDocumentCreate {
  partner_id?: number | null;
  document_type: OfficeDocumentType;
  status?: OfficeDocumentStatus;
  document_number: string;
  title: string;
  document_date: string;
  due_date?: string | null;
  amount_gross?: number;
  tax_rate?: number;
  tax_amount?: number;
  amount_net?: number;
  line_items?: OfficeLineItem[];
  notes?: string;
  receipt_id?: number | null;
  cashbook_entry_id?: number | null;
}

export type OfficeDocumentUpdate = Partial<OfficeDocumentCreate>;

export interface OfficeMonthlySummary {
  month: number;
  income: number;
  expenses: number;
  balance: number;
}

export interface OfficeCategorySummary {
  category: string;
  income: number;
  expenses: number;
}

export interface OfficeDashboard {
  year: number;
  month: number | null;
  income: number;
  expenses: number;
  balance: number;
  monthly: OfficeMonthlySummary[];
  categories: OfficeCategorySummary[];
}

export interface ContentSection {
  id?: number;
  sort_order: number;
  heading: string;
  body: string;
}

export interface ContentPage {
  id: number;
  slug: string;
  locale: string;
  title: string;
  eyebrow: string | null;
  lead: string | null;
  cta_label: string | null;
  cta_link: string | null;
  status: 'draft' | 'published';
  updated_by_user_id: number | null;
  created_at: string;
  updated_at: string | null;
  sections: ContentSection[];
}

export interface ContentPageCreate {
  slug: string;
  locale: string;
  title: string;
  eyebrow?: string;
  lead?: string;
  cta_label?: string;
  cta_link?: string;
  status?: 'draft' | 'published';
  sections?: ContentSection[];
}

export type ContentPageUpdate = Partial<Omit<ContentPageCreate, 'slug' | 'locale'>>;

export interface AppText {
  id: number;
  key: string;
  locale: 'de' | 'en' | string;
  value: string;
  status: 'draft' | 'published';
  updated_by_user_id: number | null;
  created_at: string;
  updated_at: string | null;
}

export interface AppTextCreate {
  key: string;
  locale: string;
  value: string;
  status?: 'draft' | 'published';
}

export type AppTextUpdate = Partial<Omit<AppTextCreate, 'key' | 'locale'>>;

export interface AdminUserUpdate {
  is_active?: boolean;
  is_verified?: boolean;
  is_admin?: boolean;
}

export interface DashboardSummary {
  apiary_count: number;
  hive_count: number;
  open_task_count: number;
  overdue_task_count: number;
  tasks_due_this_week: number;
  treatment_count: number;
  harvest_kg_total: number;
  inventory_item_count: number;
  latest_inspection_date: string | null;
  hives: DashboardHiveStatus[];
  apiaries: { id: number; stock_number: string; name: string | null; hive_count: number; address: string | null }[];
  open_tasks: { id: number; title: string; due_date: string | null; priority: TaskPriority; apiary_id: number | null; hive_id: number | null }[];
  upcoming_appointments: { id: number; title: string; due_date: string | null; start_at: string | null; apiary_id: number | null; hive_id: number | null }[];
  low_inventory: { id: number; name: string; category: ArticleCategory; quantity: number; unit: string }[];
}

export interface TimelineEvent {
  type: 'inspection' | 'task' | 'treatment' | 'harvest' | 'photo' | 'feeding' | string;
  id: number;
  date: string;
  title: string;
  notes?: string | null;
  status?: string;
  warnings?: string[];
  amount_kg?: number;
  amount_kg_or_l?: number;
  caption?: string | null;
  mite_count?: number | null;
  mites_per_day?: number | null;
  editable?: boolean;
  deletable?: boolean;
}

export interface StockCard {
  hive: unknown;
  qr_url: string;
  events: TimelineEvent[];
}

export interface BatchActionCreate {
  hive_ids: number[];
  date: string;
  notes?: string;
  queen_seen?: boolean;
  brood_strength?: number | null;
  varroa_count?: number | null;
  food_stores?: number | null;
  product?: string;
  method?: string;
  dosage?: string;
  feed_type?: string;
  amount_kg_or_l?: number | null;
  crop_type?: string;
  amount_kg?: number | null;
  batch_code?: string;
  target_apiary_id?: number;
  reason?: string;
}
