import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { MapService } from '../../core/services/map.service';
import { MapComponent } from './map.component';

describe('MapComponent', () => {
  const mapServiceMock = {
    getApiaryMarkers: vi.fn().mockReturnValue(of([])),
    getForagePlants: vi.fn().mockReturnValue(of([])),
    getApiaryWeather: vi.fn()
  };

  beforeEach(async () => {
    vi.clearAllMocks();
    mapServiceMock.getApiaryMarkers.mockReturnValue(of([]));
    mapServiceMock.getForagePlants.mockReturnValue(of([]));
    await TestBed.configureTestingModule({
      imports: [MapComponent],
      providers: [{ provide: MapService, useValue: mapServiceMock }]
    }).compileComponents();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(MapComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should update the radius selection', () => {
    const fixture = TestBed.createComponent(MapComponent);
    const component = fixture.componentInstance as unknown as { setRadius(value: number): void; radiusKm: () => number };
    component.setRadius(8);
    expect(component.radiusKm()).toBe(8);
  });
});
