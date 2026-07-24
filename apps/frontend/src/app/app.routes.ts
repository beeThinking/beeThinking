import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { adminGuard } from './core/guards/admin.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  {
    path: 'about',
    loadComponent: () => import('./pages/info-page/info-page.component').then(m => m.InfoPageComponent),
    data: { page: 'about' }
  },
  {
    path: 'contact',
    loadComponent: () => import('./pages/info-page/info-page.component').then(m => m.InfoPageComponent),
    data: { page: 'contact' }
  },
  {
    path: 'docs',
    loadComponent: () => import('./pages/info-page/info-page.component').then(m => m.InfoPageComponent),
    data: { page: 'docs' }
  },
  {
    path: 'tips',
    loadComponent: () => import('./pages/info-page/info-page.component').then(m => m.InfoPageComponent),
    data: { page: 'tips' }
  },
  {
    path: 'faq',
    loadComponent: () => import('./pages/info-page/info-page.component').then(m => m.InfoPageComponent),
    data: { page: 'faq' }
  },
  {
    path: 'support',
    loadComponent: () => import('./pages/info-page/info-page.component').then(m => m.InfoPageComponent),
    data: { page: 'support' }
  },
  {
    path: 'privacy',
    loadComponent: () => import('./pages/info-page/info-page.component').then(m => m.InfoPageComponent),
    data: { page: 'privacy' }
  },
  {
    path: 'imprint',
    loadComponent: () => import('./pages/info-page/info-page.component').then(m => m.InfoPageComponent),
    data: { page: 'imprint' }
  },
  {
    path: 'terms',
    loadComponent: () => import('./pages/info-page/info-page.component').then(m => m.InfoPageComponent),
    data: { page: 'terms' }
  },
  {
    path: 'login',
    loadComponent: () => import('./pages/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'register',
    loadComponent: () => import('./pages/register/register.component').then(m => m.RegisterComponent)
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [authGuard]
  },
  {
    path: 'apiaries',
    loadComponent: () => import('./pages/apiaries/apiaries.component').then(m => m.ApiariesComponent),
    canActivate: [authGuard]
  },
  {
    path: 'apiaries/:id',
    loadComponent: () => import('./pages/apiary-detail/apiary-detail.component').then(m => m.ApiaryDetailComponent),
    canActivate: [authGuard]
  },
  { path: 'stands/:id', redirectTo: 'apiaries/:id' },
  { path: 'stands', redirectTo: 'apiaries', pathMatch: 'full' },
  {
    path: 'stock-card/:hiveId',
    loadComponent: () => import('./pages/stock-card/stock-card.component').then(m => m.StockCardComponent),
    canActivate: [authGuard]
  },
  {
    path: 'hives/archive',
    loadComponent: () => import('./pages/hive-archive/hive-archive.component').then(m => m.HiveArchiveComponent),
    canActivate: [authGuard]
  },
  {
    path: 'hives/:id/inspect',
    loadComponent: () => import('./pages/hive-inspect/hive-inspect.component').then(m => m.HiveInspectComponent),
    canActivate: [authGuard]
  },
  {
    path: 'hives/:id',
    loadComponent: () => import('./pages/hive-detail/hive-detail.component').then(m => m.HiveDetailComponent),
    canActivate: [authGuard]
  },
  {
    path: 'hives',
    loadComponent: () => import('./pages/beehives/beehives.component').then(m => m.BeehivesComponent),
    canActivate: [authGuard]
  },
  { path: 'beehives/:id/inspect', redirectTo: 'hives/:id/inspect' },
  { path: 'beehives/:id', redirectTo: 'hives/:id' },
  { path: 'beehives', redirectTo: 'hives', pathMatch: 'full' },
  {
    path: 'scan',
    loadComponent: () => import('./pages/scan/scan.component').then(m => m.ScanComponent),
    canActivate: [authGuard]
  },
  {
    path: 'tasks',
    loadComponent: () => import('./pages/tasks/tasks.component').then(m => m.TasksComponent),
    canActivate: [authGuard]
  },
  {
    path: 'harvests',
    loadComponent: () => import('./pages/harvests/harvests.component').then(m => m.HarvestsComponent),
    canActivate: [authGuard]
  },
  {
    path: 'batches',
    loadComponent: () => import('./pages/batches/batches.component').then(m => m.BatchesComponent),
    canActivate: [authGuard]
  },
  {
    path: 'treatments',
    loadComponent: () => import('./pages/treatments/treatments.component').then(m => m.TreatmentsComponent),
    canActivate: [authGuard]
  },
  {
    path: 'feedings',
    loadComponent: () => import('./pages/feedings/feedings.component').then(m => m.FeedingsComponent),
    canActivate: [authGuard]
  },
  {
    path: 'honey-harvest',
    loadComponent: () => import('./pages/honey-harvest/honey-harvest.component').then(m => m.HoneyHarvestComponent),
    canActivate: [authGuard]
  },
  {
    path: 'appointments',
    loadComponent: () => import('./pages/appointments/appointments.component').then(m => m.AppointmentsComponent),
    canActivate: [authGuard]
  },
  {
    path: 'inventory/articles',
    loadComponent: () => import('./pages/inventory-articles/inventory-articles.component').then(m => m.InventoryArticlesComponent),
    canActivate: [authGuard]
  },
  {
    path: 'inventory/items',
    loadComponent: () => import('./pages/inventory-items/inventory-items.component').then(m => m.InventoryItemsComponent),
    canActivate: [authGuard]
  },
  {
    path: 'sales',
    loadComponent: () => import('./pages/sales/sales.component').then(m => m.SalesComponent),
    canActivate: [authGuard]
  },
  {
    path: 'sales/pos',
    loadComponent: () => import('./pages/pos/pos.component').then(m => m.PosComponent),
    canActivate: [authGuard]
  },
  {
    path: 'sales/report',
    loadComponent: () => import('./pages/sales/sales-report.component').then(m => m.SalesReportComponent),
    canActivate: [authGuard]
  },
  {
    path: 'honeybook',
    loadComponent: () => import('./pages/honeybook/honeybook.component').then(m => m.HoneybookComponent),
    canActivate: [authGuard]
  },
  {
    path: 'office/reports',
    loadComponent: () => import('./pages/reports/reports.component').then(m => m.ReportsComponent),
    canActivate: [authGuard]
  },
  {
    path: 'office',
    loadComponent: () => import('./pages/cashbook/cashbook.component').then(m => m.CashbookComponent),
    canActivate: [authGuard]
  },
  {
    path: 'office/cashbook',
    loadComponent: () => import('./pages/cashbook/cashbook.component').then(m => m.CashbookComponent),
    canActivate: [authGuard]
  },
  {
    path: 'admin/content',
    redirectTo: '/admin/cms',
    pathMatch: 'full'
  },
  {
    path: 'admin/cms',
    loadComponent: () => import('./pages/content-admin/content-admin.component').then(m => m.ContentAdminComponent),
    canActivate: [authGuard, adminGuard]
  },
  {
    path: 'inspections',
    loadComponent: () => import('./pages/inspections/inspections.component').then(m => m.InspectionsComponent),
    canActivate: [authGuard]
  },
  {
    path: 'traceability',
    loadComponent: () => import('./pages/traceability/traceability.component').then(m => m.TraceabilityComponent),
    canActivate: [authGuard]
  },
  {
    path: 'zuchtreihen',
    loadComponent: () => import('./pages/zuchtreihen/zuchtreihen.component').then(m => m.ZuchtreihenComponent),
    canActivate: [authGuard]
  },
  {
    path: 'zuchtreihen/:id',
    loadComponent: () => import('./pages/zuchtreihe-detail/zuchtreihe-detail.component').then(m => m.ZuchtreiheDetailComponent),
    canActivate: [authGuard]
  },
  {
    path: 'zucht-selektion',
    loadComponent: () => import('./pages/zucht-selektion/zucht-selektion.component').then(m => m.ZuchtSelektionComponent),
    canActivate: [authGuard]
  },
  {
    path: 'hive-selection',
    loadComponent: () => import('./pages/hive-selection/hive-selection.component').then(m => m.HiveSelectionComponent),
    canActivate: [authGuard]
  },
  {
    path: 'map',
    loadComponent: () => import('./pages/map/map.component').then(m => m.MapComponent),
    canActivate: [authGuard]
  },
  {
    path: 'feed-calculator',
    loadComponent: () => import('./pages/feed-calculator/feed-calculator.component').then(m => m.FeedCalculatorComponent)
  },
  {
    path: 'honey-price-calculator',
    loadComponent: () => import('./pages/honey-price-calculator/honey-price-calculator.component').then(m => m.HoneyPriceCalculatorComponent),
    canActivate: [authGuard]
  },
  {
    path: 'settings',
    loadComponent: () => import('./pages/settings/settings.component').then(m => m.SettingsComponent),
    canActivate: [authGuard]
  }
];
