import { effect, Injectable, inject, signal } from '@angular/core';
import { catchError, of } from 'rxjs';
import { en, TranslationKey } from '../i18n/en';
import { de } from '../i18n/de';
import { ApiService } from './api.service';

type Translations = Record<string, string>;
export type Lang = 'en' | 'de';

const TRANSLATIONS: Record<Lang, Translations> = { en: en as Translations, de: de as Translations };
const STORAGE_KEY = 'bee_lang';

function storedLang(): Lang {
  const value = globalThis.localStorage?.getItem(STORAGE_KEY);
  return value === 'en' || value === 'de' ? value : 'de';
}

@Injectable({ providedIn: 'root' })
export class TranslationService {
  private readonly api = inject(ApiService);
  private readonly overrides = signal<Translations>({});
  readonly currentLang = signal<Lang>(storedLang());

  constructor() {
    effect(() => {
      this.loadOverrides(this.currentLang());
    });
  }

  t(key: TranslationKey, params?: Record<string, string | number>): string {
    const dict = TRANSLATIONS[this.currentLang()];
    let value = this.overrides()[key] ?? dict[key] ?? (en as Translations)[key] ?? key;
    if (params) {
      for (const [k, v] of Object.entries(params)) {
        value = value.replace(`{{${k}}}`, String(v));
      }
    }
    return value;
  }

  setLang(lang: Lang): void {
    this.currentLang.set(lang);
    globalThis.localStorage?.setItem(STORAGE_KEY, lang);
  }

  toggleLang(): void {
    this.setLang(this.currentLang() === 'de' ? 'en' : 'de');
  }

  private loadOverrides(lang: Lang): void {
    this.api.get<Translations>(`/api/content/app-texts?locale=${lang}`).pipe(
      catchError(() => of({}))
    ).subscribe(overrides => this.overrides.set(overrides));
  }
}
