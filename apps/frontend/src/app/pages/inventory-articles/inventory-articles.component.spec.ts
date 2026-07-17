import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { Article } from '../../core/models/beekeeping.models';
import { BeekeepingService } from '../../core/services/beekeeping.service';
import { InventoryArticlesComponent } from './inventory-articles.component';

describe('InventoryArticlesComponent', () => {
  const articles: Partial<Article>[] = [
    { id: 1, name: 'Neutralglas 500g', category: 'honey', unit: 'piece' },
    { id: 2, name: 'Futterteig', category: 'feed', unit: 'kg' }
  ];

  const beekeepingServiceMock = {
    getArticles: vi.fn().mockReturnValue(of(articles)),
    createArticle: vi.fn().mockReturnValue(of(articles[0])),
    deleteArticle: vi.fn().mockReturnValue(of(void 0))
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InventoryArticlesComponent],
      providers: [{ provide: BeekeepingService, useValue: beekeepingServiceMock }]
    }).compileComponents();

    vi.clearAllMocks();
    beekeepingServiceMock.getArticles.mockReturnValue(of(articles));
    beekeepingServiceMock.createArticle.mockReturnValue(of(articles[0]));
    beekeepingServiceMock.deleteArticle.mockReturnValue(of(void 0));
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(InventoryArticlesComponent);

    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should render loaded articles', () => {
    const fixture = TestBed.createComponent(InventoryArticlesComponent);
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.textContent).toContain('Neutralglas 500g');
    expect(element.textContent).toContain('Futterteig');
  });

  it('should not create an article without a name', () => {
    const fixture = TestBed.createComponent(InventoryArticlesComponent);
    const component = fixture.componentInstance as unknown as { create: () => void };

    component.create();

    expect(beekeepingServiceMock.createArticle).not.toHaveBeenCalled();
  });

  it('should create an article and reload the list', () => {
    const fixture = TestBed.createComponent(InventoryArticlesComponent);
    const component = fixture.componentInstance as unknown as {
      create: () => void;
      name: { set: (value: string) => void };
    };

    component.name.set('Honigglas 250g');
    component.create();

    expect(beekeepingServiceMock.createArticle).toHaveBeenCalledTimes(1);
    expect(beekeepingServiceMock.getArticles).toHaveBeenCalledTimes(2);
  });

  it('should delete an article and reload the list', () => {
    const fixture = TestBed.createComponent(InventoryArticlesComponent);
    const component = fixture.componentInstance as unknown as {
      delete: (article: Partial<Article>) => void;
    };

    component.delete(articles[0]);

    expect(beekeepingServiceMock.deleteArticle).toHaveBeenCalledWith(1);
    expect(beekeepingServiceMock.getArticles).toHaveBeenCalledTimes(2);
  });
});
