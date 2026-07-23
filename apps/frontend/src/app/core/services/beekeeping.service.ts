import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import {
  DashboardSummary,
  Article,
  ArticleCreate,
  ArticleUpdate,
  AdminUserUpdate,
  AppText,
  AppTextCreate,
  AppTextUpdate,
  Batch,
  BatchCreate,
  BatchUpdate,
  CashbookEntry,
  CashbookEntryCreate,
  CashbookEntryUpdate,
  CashbookSummary,
  ContentPage,
  ContentPageCreate,
  ContentPageUpdate,
  Feeding,
  FeedingCreate,
  FeedingUpdate,
  Harvest,
  HarvestCreate,
  HarvestUpdate,
  InventoryItem,
  InventoryItemCreate,
  InventoryItemUpdate,
  OfficeDashboard,
  OfficeDocument,
  OfficeDocumentCreate,
  OfficeDocumentType,
  OfficeDocumentUpdate,
  OfficePartner,
  OfficePartnerCreate,
  OfficePartnerType,
  OfficePartnerUpdate,
  Photo,
  PhotoPreview,
  Task,
  TaskCreate,
  TaskStatus,
  TaskUpdate,
  Treatment,
  TreatmentCreate,
  TreatmentUpdate
} from '../models/beekeeping.models';
import { UserResponse } from '../models/auth.models';

@Injectable({ providedIn: 'root' })
export class BeekeepingService {
  private readonly api = inject(ApiService);

  getDashboardSummary(): Observable<DashboardSummary> {
    return this.api.get<DashboardSummary>('/api/dashboard/summary');
  }

  getTasks(status?: TaskStatus): Observable<Task[]> {
    const query = status ? `?task_status=${status}` : '';
    return this.api.get<Task[]>(`/api/tasks${query}`);
  }

  createTask(task: TaskCreate): Observable<Task> {
    return this.api.post<Task>('/api/tasks', task);
  }

  updateTask(id: number, task: TaskUpdate): Observable<Task> {
    return this.api.put<Task>(`/api/tasks/${id}`, task);
  }

  completeTask(id: number): Observable<Task> {
    return this.api.post<Task>(`/api/tasks/${id}/complete`, {});
  }

  deleteTask(id: number): Observable<void> {
    return this.api.delete<void>(`/api/tasks/${id}`);
  }

  getTreatments(): Observable<Treatment[]> {
    return this.api.get<Treatment[]>('/api/treatments');
  }

  createTreatment(treatment: TreatmentCreate): Observable<Treatment> {
    return this.api.post<Treatment>('/api/treatments', treatment);
  }

  updateTreatment(id: number, treatment: TreatmentUpdate): Observable<Treatment> {
    return this.api.put<Treatment>(`/api/treatments/${id}`, treatment);
  }

  deleteTreatment(id: number): Observable<void> {
    return this.api.delete<void>(`/api/treatments/${id}`);
  }

  getHarvests(): Observable<Harvest[]> {
    return this.api.get<Harvest[]>('/api/harvests');
  }

  createHarvest(harvest: HarvestCreate): Observable<Harvest> {
    return this.api.post<Harvest>('/api/harvests', harvest);
  }

  updateHarvest(id: number, harvest: HarvestUpdate): Observable<Harvest> {
    return this.api.put<Harvest>(`/api/harvests/${id}`, harvest);
  }

  deleteHarvest(id: number): Observable<void> {
    return this.api.delete<void>(`/api/harvests/${id}`);
  }

  getBatches(): Observable<Batch[]> {
    return this.api.get<Batch[]>('/api/batches');
  }

  getBatch(id: number): Observable<Batch> {
    return this.api.get<Batch>(`/api/batches/${id}`);
  }

  createBatch(batch: BatchCreate): Observable<Batch> {
    return this.api.post<Batch>('/api/batches', batch);
  }

  updateBatch(id: number, batch: BatchUpdate): Observable<Batch> {
    return this.api.put<Batch>(`/api/batches/${id}`, batch);
  }

  deleteBatch(id: number): Observable<void> {
    return this.api.delete<void>(`/api/batches/${id}`);
  }

  attachHarvestToBatch(batchId: number, harvestId: number): Observable<Batch> {
    return this.api.post<Batch>(`/api/batches/${batchId}/harvests/${harvestId}`, {});
  }

  detachHarvestFromBatch(batchId: number, harvestId: number): Observable<Batch> {
    return this.api.delete<Batch>(`/api/batches/${batchId}/harvests/${harvestId}`);
  }

  getFeedings(): Observable<Feeding[]> {
    return this.api.get<Feeding[]>('/api/feedings');
  }

  createFeeding(feeding: FeedingCreate): Observable<Feeding> {
    return this.api.post<Feeding>('/api/feedings', feeding);
  }

  updateFeeding(id: number, feeding: FeedingUpdate): Observable<Feeding> {
    return this.api.put<Feeding>(`/api/feedings/${id}`, feeding);
  }

  deleteFeeding(id: number): Observable<void> {
    return this.api.delete<void>(`/api/feedings/${id}`);
  }

  getArticles(): Observable<Article[]> {
    return this.api.get<Article[]>('/api/articles');
  }

  createArticle(article: ArticleCreate): Observable<Article> {
    return this.api.post<Article>('/api/articles', article);
  }

  updateArticle(id: number, article: ArticleUpdate): Observable<Article> {
    return this.api.put<Article>(`/api/articles/${id}`, article);
  }

  deleteArticle(id: number): Observable<void> {
    return this.api.delete<void>(`/api/articles/${id}`);
  }

  getInventoryItems(): Observable<InventoryItem[]> {
    return this.api.get<InventoryItem[]>('/api/inventory-items');
  }

  createInventoryItem(item: InventoryItemCreate): Observable<InventoryItem> {
    return this.api.post<InventoryItem>('/api/inventory-items', item);
  }

  updateInventoryItem(id: number, item: InventoryItemUpdate): Observable<InventoryItem> {
    return this.api.put<InventoryItem>(`/api/inventory-items/${id}`, item);
  }

  deleteInventoryItem(id: number): Observable<void> {
    return this.api.delete<void>(`/api/inventory-items/${id}`);
  }

  getReport<T>(name: 'harvest-by-crop' | 'harvest-by-apiary' | 'varroa' | 'feedings', from?: string, to?: string): Observable<T[]> {
    const params = new URLSearchParams();
    if (from) params.set('from_date', from);
    if (to) params.set('to_date', to);
    const query = params.toString();
    return this.api.get<T[]>(`/api/reports/${name}${query ? `?${query}` : ''}`);
  }

  getPhotos(): Observable<Photo[]> {
    return this.api.get<Photo[]>('/api/photos');
  }

  getCashbookEntries(from?: string, to?: string): Observable<CashbookEntry[]> {
    const params = new URLSearchParams();
    if (from) params.set('from_date', from);
    if (to) params.set('to_date', to);
    const query = params.toString();
    return this.api.get<CashbookEntry[]>(`/api/cashbook/entries${query ? `?${query}` : ''}`);
  }

  createCashbookEntry(entry: CashbookEntryCreate): Observable<CashbookEntry> {
    return this.api.post<CashbookEntry>('/api/cashbook/entries', entry);
  }

  updateCashbookEntry(id: number, entry: CashbookEntryUpdate): Observable<CashbookEntry> {
    return this.api.put<CashbookEntry>(`/api/cashbook/entries/${id}`, entry);
  }

  deleteCashbookEntry(id: number): Observable<void> {
    return this.api.delete<void>(`/api/cashbook/entries/${id}`);
  }

  getCashbookSummary(from?: string, to?: string): Observable<CashbookSummary> {
    const params = new URLSearchParams();
    if (from) params.set('from_date', from);
    if (to) params.set('to_date', to);
    const query = params.toString();
    return this.api.get<CashbookSummary>(`/api/cashbook/summary${query ? `?${query}` : ''}`);
  }

  getOfficeDashboard(year: number, month?: number | null): Observable<OfficeDashboard> {
    const params = new URLSearchParams({ year: String(year) });
    if (month) params.set('month', String(month));
    return this.api.get<OfficeDashboard>(`/api/office/dashboard?${params.toString()}`);
  }

  getOfficePartners(type?: OfficePartnerType): Observable<OfficePartner[]> {
    const query = type ? `?partner_type=${type}` : '';
    return this.api.get<OfficePartner[]>(`/api/office/partners${query}`);
  }

  createOfficePartner(partner: OfficePartnerCreate): Observable<OfficePartner> {
    return this.api.post<OfficePartner>('/api/office/partners', partner);
  }

  updateOfficePartner(id: number, partner: OfficePartnerUpdate): Observable<OfficePartner> {
    return this.api.put<OfficePartner>(`/api/office/partners/${id}`, partner);
  }

  deleteOfficePartner(id: number): Observable<void> {
    return this.api.delete<void>(`/api/office/partners/${id}`);
  }

  getOfficeDocuments(type?: OfficeDocumentType): Observable<OfficeDocument[]> {
    const query = type ? `?document_type=${type}` : '';
    return this.api.get<OfficeDocument[]>(`/api/office/documents${query}`);
  }

  createOfficeDocument(document: OfficeDocumentCreate): Observable<OfficeDocument> {
    return this.api.post<OfficeDocument>('/api/office/documents', document);
  }

  updateOfficeDocument(id: number, document: OfficeDocumentUpdate): Observable<OfficeDocument> {
    return this.api.put<OfficeDocument>(`/api/office/documents/${id}`, document);
  }

  deleteOfficeDocument(id: number): Observable<void> {
    return this.api.delete<void>(`/api/office/documents/${id}`);
  }

  downloadOfficeCsv(year: number): Observable<Blob> {
    return this.api.getBlob(`/api/office/cashbook/export.csv?year=${year}`);
  }

  downloadOfficePdf(year: number): Observable<Blob> {
    return this.api.getBlob(`/api/office/cashbook/report.pdf?year=${year}`);
  }

  getContentPages(): Observable<ContentPage[]> {
    return this.api.get<ContentPage[]>('/api/admin/content/pages');
  }

  getContentPage(slug: string, locale: string): Observable<ContentPage> {
    return this.api.get<ContentPage>(`/api/content/pages/${slug}?locale=${locale}`);
  }

  createContentPage(page: ContentPageCreate): Observable<ContentPage> {
    return this.api.post<ContentPage>('/api/admin/content/pages', page);
  }

  updateContentPage(id: number, page: ContentPageUpdate): Observable<ContentPage> {
    return this.api.put<ContentPage>(`/api/admin/content/pages/${id}`, page);
  }

  getAppTexts(): Observable<AppText[]> {
    return this.api.get<AppText[]>('/api/admin/content/app-texts');
  }

  upsertAppText(text: AppTextCreate): Observable<AppText> {
    return this.api.post<AppText>('/api/admin/content/app-texts', text);
  }

  updateAppText(id: number, text: AppTextUpdate): Observable<AppText> {
    return this.api.put<AppText>(`/api/admin/content/app-texts/${id}`, text);
  }

  getAdminUsers(search?: string): Observable<UserResponse[]> {
    const query = search ? `?search=${encodeURIComponent(search)}` : '';
    return this.api.get<UserResponse[]>(`/api/users${query}`);
  }

  updateAdminUser(id: number, update: AdminUserUpdate): Observable<UserResponse> {
    return this.api.patch<UserResponse>(`/api/users/${id}`, update);
  }

  uploadPhoto(input: { file: File; hive_id?: number; inspection_id?: number; caption?: string }): Observable<Photo> {
    const form = new FormData();
    form.append('file', input.file);
    if (input.hive_id) {
      form.append('hive_id', String(input.hive_id));
    }
    if (input.inspection_id) {
      form.append('inspection_id', String(input.inspection_id));
    }
    if (input.caption?.trim()) {
      form.append('caption', input.caption.trim());
    }
    return this.api.post<Photo>('/api/photos/upload', form);
  }

  getPhotoPreview(id: number): Observable<PhotoPreview> {
    return this.api.get<PhotoPreview>(`/api/photos/${id}/preview`);
  }

  deletePhoto(id: number): Observable<void> {
    return this.api.delete<void>(`/api/photos/${id}`);
  }

  createBatchAction(
    apiaryId: number,
    actionType: string,
    payload: {
      hive_ids: number[];
      date: string;
      notes?: string;
      feed_type?: string;
      amount_kg_or_l?: number;
      product?: string;
      target_apiary_id?: number;
    }
  ): Observable<{ action_type: string; created: number; hive_ids: number[] }> {
    return this.api.post<{ action_type: string; created: number; hive_ids: number[] }>(
      `/api/apiaries/${apiaryId}/batch-actions/${actionType}`,
      payload
    );
  }
}
