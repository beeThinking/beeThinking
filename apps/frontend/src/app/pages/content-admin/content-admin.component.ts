import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormArray, FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { UserResponse } from '../../core/models/auth.models';
import { AppText, ContentPage } from '../../core/models/beekeeping.models';
import { de } from '../../core/i18n/de';
import { en } from '../../core/i18n/en';
import { BeekeepingService } from '../../core/services/beekeeping.service';

type CmsTab = 'pages' | 'texts' | 'users';
type Locale = 'de' | 'en';

interface TranslationRow {
  key: string;
  deDefault: string;
  enDefault: string;
  deOverride: AppText | null;
  enOverride: AppText | null;
}

@Component({
  selector: 'app-content-admin',
  standalone: true,
  imports: [DatePipe, ReactiveFormsModule],
  templateUrl: './content-admin.component.html',
  styleUrl: './content-admin.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ContentAdminComponent {
  private readonly beekeeping = inject(BeekeepingService);
  private readonly fb = inject(FormBuilder);

  protected readonly tab = signal<CmsTab>('pages');
  protected readonly pages = signal<ContentPage[]>([]);
  protected readonly appTexts = signal<AppText[]>([]);
  protected readonly users = signal<UserResponse[]>([]);
  protected readonly selectedPageId = signal<number | null>(null);
  protected readonly userSearch = signal('');
  protected readonly textSearch = signal('');
  protected readonly errorMessage = signal('');
  protected readonly successMessage = signal('');

  protected readonly tabs: { id: CmsTab; label: string }[] = [
    { id: 'pages', label: 'Seiten' },
    { id: 'texts', label: 'App-Texte' },
    { id: 'users', label: 'User' }
  ];

  protected readonly pageForm = this.fb.group({
    slug: ['', [Validators.required, Validators.maxLength(120)]],
    locale: ['de' as Locale, Validators.required],
    title: ['', [Validators.required, Validators.maxLength(200)]],
    eyebrow: [''],
    lead: [''],
    cta_label: [''],
    cta_link: [''],
    status: ['draft' as 'draft' | 'published', Validators.required],
    sections: this.fb.array([
      this.fb.group({
        sort_order: [0],
        heading: ['', Validators.required],
        body: ['', Validators.required]
      })
    ])
  });

  protected readonly textForm = this.fb.group({
    key: ['', [Validators.required, Validators.maxLength(200)]],
    locale: ['de' as Locale, Validators.required],
    value: ['', Validators.required],
    status: ['draft' as 'draft' | 'published', Validators.required]
  });

  protected readonly filteredTranslationRows = computed(() => {
    const query = this.textSearch().trim().toLowerCase();
    const rows = this.translationRows();
    if (!query) return rows;
    return rows.filter(row =>
      row.key.toLowerCase().includes(query) ||
      row.deDefault.toLowerCase().includes(query) ||
      row.enDefault.toLowerCase().includes(query)
    );
  });

  private readonly translationRows = computed<TranslationRow[]>(() => {
    const keys = Array.from(new Set([...Object.keys(de), ...Object.keys(en)])).sort();
    return keys.map(key => ({
      key,
      deDefault: (de as Record<string, string>)[key] ?? '',
      enDefault: (en as Record<string, string>)[key] ?? '',
      deOverride: this.findAppText(key, 'de'),
      enOverride: this.findAppText(key, 'en')
    }));
  });

  constructor() {
    this.loadAll();
  }

  protected get sections(): FormArray {
    return this.pageForm.controls.sections;
  }

  protected setTab(tab: CmsTab): void {
    this.tab.set(tab);
    this.errorMessage.set('');
    this.successMessage.set('');
  }

  protected addSection(): void {
    this.sections.push(this.fb.group({
      sort_order: [this.sections.length],
      heading: ['', Validators.required],
      body: ['', Validators.required]
    }));
  }

  protected removeSection(index: number): void {
    if (this.sections.length <= 1) return;
    this.sections.removeAt(index);
  }

  protected newPage(): void {
    this.selectedPageId.set(null);
    this.pageForm.reset({ locale: 'de', status: 'draft' });
    this.sections.clear();
    this.addSection();
  }

  protected editPage(page: ContentPage): void {
    this.selectedPageId.set(page.id);
    this.pageForm.reset({
      slug: page.slug,
      locale: page.locale as Locale,
      title: page.title,
      eyebrow: page.eyebrow ?? '',
      lead: page.lead ?? '',
      cta_label: page.cta_label ?? '',
      cta_link: page.cta_link ?? '',
      status: page.status
    });
    this.sections.clear();
    for (const section of page.sections.length ? page.sections : [{ sort_order: 0, heading: '', body: '' }]) {
      this.sections.push(this.fb.group({
        sort_order: [section.sort_order],
        heading: [section.heading, Validators.required],
        body: [section.body, Validators.required]
      }));
    }
  }

  protected savePage(): void {
    if (this.pageForm.invalid) return;
    const value = this.pageForm.value;
    const body = {
      slug: value.slug!,
      locale: value.locale!,
      title: value.title!,
      eyebrow: value.eyebrow || undefined,
      lead: value.lead || undefined,
      cta_label: value.cta_label || undefined,
      cta_link: value.cta_link || undefined,
      status: value.status!,
      sections: (value.sections ?? []).map((section, index) => ({
        sort_order: Number(section?.sort_order ?? index),
        heading: section?.heading ?? '',
        body: section?.body ?? ''
      }))
    };
    const selectedId = this.selectedPageId();
    const request = selectedId
      ? this.beekeeping.updateContentPage(selectedId, body)
      : this.beekeeping.createContentPage(body);
    request.subscribe({
      next: page => {
        this.successMessage.set('Seite gespeichert.');
        this.loadPages();
        this.editPage(page);
      },
      error: () => this.errorMessage.set('CMS-Seite konnte nicht gespeichert werden.')
    });
  }

  protected selectText(key: string, locale: Locale): void {
    const existing = this.findAppText(key, locale);
    this.textForm.reset({
      key,
      locale,
      value: existing?.value ?? this.defaultText(key, locale),
      status: existing?.status ?? 'draft'
    });
  }

  protected saveText(): void {
    if (this.textForm.invalid) return;
    const value = this.textForm.value;
    this.beekeeping.upsertAppText({
      key: value.key!,
      locale: value.locale!,
      value: value.value!,
      status: value.status!
    }).subscribe({
      next: () => {
        this.successMessage.set('App-Text gespeichert.');
        this.loadAppTexts();
      },
      error: () => this.errorMessage.set('App-Text konnte nicht gespeichert werden.')
    });
  }

  protected toggleUser(user: UserResponse, field: 'is_active' | 'is_verified' | 'is_admin'): void {
    this.beekeeping.updateAdminUser(user.id, { [field]: !user[field] }).subscribe({
      next: updated => this.users.update(users => users.map(item => item.id === updated.id ? updated : item)),
      error: () => this.errorMessage.set('User konnte nicht aktualisiert werden.')
    });
  }

  protected searchUsers(): void {
    this.loadUsers(this.userSearch());
  }

  protected statusLabel(status: 'draft' | 'published'): string {
    return status === 'published' ? 'Veröffentlicht' : 'Entwurf';
  }

  protected defaultText(key: string, locale: Locale): string {
    return locale === 'de' ? (de as Record<string, string>)[key] ?? '' : (en as Record<string, string>)[key] ?? '';
  }

  private loadAll(): void {
    this.loadPages();
    this.loadAppTexts();
    this.loadUsers();
  }

  private loadPages(): void {
    this.beekeeping.getContentPages().subscribe({
      next: pages => this.pages.set(pages),
      error: () => this.errorMessage.set('CMS-Seiten konnten nicht geladen werden.')
    });
  }

  private loadAppTexts(): void {
    this.beekeeping.getAppTexts().subscribe({
      next: texts => this.appTexts.set(texts),
      error: () => this.errorMessage.set('App-Texte konnten nicht geladen werden.')
    });
  }

  private loadUsers(search = ''): void {
    this.beekeeping.getAdminUsers(search.trim() || undefined).subscribe({
      next: users => this.users.set(users),
      error: () => this.errorMessage.set('User konnten nicht geladen werden.')
    });
  }

  private findAppText(key: string, locale: Locale): AppText | null {
    return this.appTexts().find(text => text.key === key && text.locale === locale) ?? null;
  }
}
