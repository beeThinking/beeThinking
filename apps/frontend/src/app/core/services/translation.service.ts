import { Injectable, signal } from '@angular/core';
import { en, TranslationKey } from '../i18n/en';
import { de } from '../i18n/de';

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
  readonly currentLang = signal<Lang>(storedLang());

  t(key: TranslationKey, params?: Record<string, string | number>): string {
    const dict = TRANSLATIONS[this.currentLang()];
    let value = dict[key] ?? (en as Translations)[key] ?? key;
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
}
