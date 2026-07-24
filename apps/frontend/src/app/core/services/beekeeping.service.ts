import { Injectable, inject } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { Observable, catchError, of, throwError } from 'rxjs';
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
  BottleRequest,
  BottleResponse,
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
  HoneybookEntry,
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
  Sale,
  SaleCreate,
  SaleReportRow,
  Task,
  TaskCreate,
  TaskOccurrence,
  TaskStatus,
  TaskUpdate,
  TraceabilityResponse,
  Treatment,
  TreatmentCreate,
  TreatmentUpdate
} from '../models/beekeeping.models';
import { UserResponse } from '../models/auth.models';
import {
  BreedingCandidate,
  BreedingStep,
  BreedingStepCreate,
  BreedingStepUpdate,
  CriterionWeight,
  CriterionWeightUpsert,
  Zuchtreihe,
  ZuchtreiheCreate,
  ZuchtreiheUpdate
} from '../models/breeding.models';

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

  getTaskOccurrences(rangeStart?: string, rangeEnd?: string, status?: TaskStatus): Observable<TaskOccurrence[]> {
    const params = new URLSearchParams();
    if (rangeStart) params.set('range_start', rangeStart);
    if (rangeEnd) params.set('range_end', rangeEnd);
    if (status) params.set('task_status', status);
    const query = params.toString();
    return this.api.get<TaskOccurrence[]>(`/api/tasks/occurrences${query ? `?${query}` : ''}`);
  }

  delegateTask(id: number, assigneeId: number): Observable<Task> {
    return this.api.post<Task>(`/api/tasks/${id}/delegate`, { assignee_id: assigneeId });
  }

  acknowledgeTaskDelegation(id: number): Observable<Task> {
    return this.api.post<Task>(`/api/tasks/${id}/delegation-seen`, {});
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

  downloadTreatmentJournalPdf(year: number): Observable<Blob> {
    return this.api.getBlob(`/api/treatments/journal/export.pdf?year=${year}`);
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

  bottleBatch(batchId: number, request: BottleRequest): Observable<BottleResponse> {
    return this.api.post<BottleResponse>(`/api/batches/${batchId}/bottle`, request);
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

  downloadInventoryMaterialPdf(): Observable<Blob> {
    return this.api.getBlob('/api/reports/inventory-material.pdf');
  }

  downloadInventoryFinishedGoodsPdf(): Observable<Blob> {
    return this.api.getBlob('/api/reports/inventory-finished-goods.pdf');
  }

  downloadFeedingsPdf(from?: string, to?: string): Observable<Blob> {
    const params = new URLSearchParams();
    if (from) params.set('from_date', from);
    if (to) params.set('to_date', to);
    const query = params.toString();
    return this.api.getBlob(`/api/reports/feedings.pdf${query ? `?${query}` : ''}`);
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

  downloadCustomerListPdf(): Observable<Blob> {
    return this.api.getBlob('/api/office/partners/customers.pdf');
  }

  getSales(): Observable<Sale[]> {
    return this.api.get<Sale[]>('/api/sales');
  }

  getSale(id: number): Observable<Sale> {
    return this.api.get<Sale>(`/api/sales/${id}`);
  }

  createSale(sale: SaleCreate): Observable<Sale> {
    return this.api.post<Sale>('/api/sales', sale);
  }

  deleteSale(id: number): Observable<void> {
    return this.api.delete<void>(`/api/sales/${id}`);
  }

  getSalesReport(fromDate?: string, toDate?: string): Observable<SaleReportRow[]> {
    const params = new URLSearchParams();
    if (fromDate) params.set('from_date', fromDate);
    if (toDate) params.set('to_date', toDate);
    const query = params.toString();
    return this.api.get<SaleReportRow[]>(`/api/sales/report${query ? `?${query}` : ''}`);
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

  getHoneybookRegister(year?: number): Observable<HoneybookEntry[]> {
    const query = year ? `?year=${year}` : '';
    return this.api.get<HoneybookEntry[]>(`/api/honeybook/register${query}`);
  }

  downloadHoneybookPdf(year?: number): Observable<Blob> {
    const query = year ? `?year=${year}` : '';
    return this.api.getBlob(`/api/honeybook/register.pdf${query}`);
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

  getTraceability(lotNumber: string): Observable<TraceabilityResponse | null> {
    return this.api.get<TraceabilityResponse>(`/api/traceability/${encodeURIComponent(lotNumber)}`).pipe(
      catchError((error: unknown) => {
        if (error instanceof HttpErrorResponse && error.status === 404) {
          return of(null);
        }
        return throwError(() => error);
      })
    );
  }

  getZuchtreihen(apiaryId?: number): Observable<Zuchtreihe[]> {
    const query = apiaryId ? `?apiary_id=${apiaryId}` : '';
    return this.api.get<Zuchtreihe[]>(`/api/zuchtreihen${query}`);
  }

  getZuchtreihe(id: number): Observable<Zuchtreihe> {
    return this.api.get<Zuchtreihe>(`/api/zuchtreihen/${id}`);
  }

  createZuchtreihe(zuchtreihe: ZuchtreiheCreate): Observable<Zuchtreihe> {
    return this.api.post<Zuchtreihe>('/api/zuchtreihen', zuchtreihe);
  }

  updateZuchtreihe(id: number, zuchtreihe: ZuchtreiheUpdate): Observable<Zuchtreihe> {
    return this.api.put<Zuchtreihe>(`/api/zuchtreihen/${id}`, zuchtreihe);
  }

  deleteZuchtreihe(id: number): Observable<void> {
    return this.api.delete<void>(`/api/zuchtreihen/${id}`);
  }

  getBreedingSteps(zuchtreiheId: number): Observable<BreedingStep[]> {
    return this.api.get<BreedingStep[]>(`/api/zuchtreihen/${zuchtreiheId}/steps`);
  }

  generateBreedingSteps(zuchtreiheId: number, umlarvenDate: string): Observable<BreedingStep[]> {
    return this.api.post<BreedingStep[]>(`/api/zuchtreihen/${zuchtreiheId}/steps/generate`, { umlarven_date: umlarvenDate });
  }

  createBreedingStep(zuchtreiheId: number, step: BreedingStepCreate): Observable<BreedingStep> {
    return this.api.post<BreedingStep>(`/api/zuchtreihen/${zuchtreiheId}/steps`, step);
  }

  updateBreedingStep(zuchtreiheId: number, stepId: number, step: BreedingStepUpdate): Observable<BreedingStep> {
    return this.api.put<BreedingStep>(`/api/zuchtreihen/${zuchtreiheId}/steps/${stepId}`, step);
  }

  deleteBreedingStep(zuchtreiheId: number, stepId: number): Observable<void> {
    return this.api.delete<void>(`/api/zuchtreihen/${zuchtreiheId}/steps/${stepId}`);
  }

  getCriterionWeights(): Observable<CriterionWeight[]> {
    return this.api.get<CriterionWeight[]>('/api/breeding-selection/weights');
  }

  upsertCriterionWeight(payload: CriterionWeightUpsert): Observable<CriterionWeight> {
    return this.api.put<CriterionWeight>('/api/breeding-selection/weights', payload);
  }

  deleteCriterionWeight(criterionId: number): Observable<void> {
    return this.api.delete<void>(`/api/breeding-selection/weights/${criterionId}`);
  }

  getBreedingCandidates(): Observable<BreedingCandidate[]> {
    return this.api.get<BreedingCandidate[]>('/api/breeding-selection/candidates');
  }
}
