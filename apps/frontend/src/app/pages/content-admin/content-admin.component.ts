import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormArray, FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { ContentPage } from '../../core/models/beekeeping.models';
import { BeekeepingService } from '../../core/services/beekeeping.service';

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

  protected readonly pages = signal<ContentPage[]>([]);
  protected readonly errorMessage = signal('');

  protected readonly form = this.fb.group({
    slug: ['', Validators.required],
    locale: ['de', Validators.required],
    title: ['', Validators.required],
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

  constructor() {
    this.load();
  }

  protected get sections(): FormArray {
    return this.form.controls.sections;
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

  protected load(): void {
    this.beekeeping.getContentPages().subscribe({
      next: pages => this.pages.set(pages),
      error: () => this.errorMessage.set('CMS-Seiten konnten nicht geladen werden.')
    });
  }

  protected createPage(): void {
    if (this.form.invalid) return;
    const value = this.form.value;
    this.beekeeping.createContentPage({
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
    }).subscribe({
      next: () => {
        this.form.reset({ locale: 'de', status: 'draft' });
        this.load();
      },
      error: () => this.errorMessage.set('CMS-Seite konnte nicht gespeichert werden.')
    });
  }
}
