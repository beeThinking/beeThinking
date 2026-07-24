import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  OnDestroy,
  ViewChild,
  inject,
  signal
} from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { forkJoin } from 'rxjs';

import { ApiaryMapMarker, ApiaryWeatherForecast, ForagePlantEntry } from '../../core/models/map.models';
import { MapService } from '../../core/services/map.service';
import { TranslationService } from '../../core/services/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';

import type * as Leaflet from 'leaflet';

@Component({
  selector: 'app-map',
  standalone: true,
  imports: [DatePipe, FormsModule, TranslatePipe],
  templateUrl: './map.component.html',
  styleUrl: './map.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class MapComponent implements AfterViewInit, OnDestroy {
  private readonly mapService = inject(MapService);
  private readonly translation = inject(TranslationService);

  @ViewChild('mapContainer', { static: true }) private mapContainer?: ElementRef<HTMLDivElement>;

  protected readonly radiusKm = signal(3);
  protected readonly forageVisible = signal(false);
  protected readonly selectedWeather = signal<ApiaryWeatherForecast | null>(null);
  protected readonly loadError = signal('');
  protected readonly loading = signal(true);

  private leaflet?: typeof Leaflet;
  private map?: Leaflet.Map;
  private radiusCircle?: Leaflet.Circle;
  private forageLayer?: Leaflet.LayerGroup;
  private markers: ApiaryMapMarker[] = [];
  private foragePlants: ForagePlantEntry[] = [];
  private resizeObserver?: ResizeObserver;

  async ngAfterViewInit(): Promise<void> {
    try {
      const leafletModule = await import('leaflet');
      this.leaflet = (leafletModule.default ?? leafletModule) as typeof Leaflet;
      this.createMap();
      this.resizeObserver = new ResizeObserver(() => this.map?.invalidateSize());
      this.resizeObserver.observe(this.mapContainer!.nativeElement);
      this.loadData();
    } catch {
      this.loadError.set(this.translation.t('mapPage.error.load'));
      this.loading.set(false);
    }
  }

  ngOnDestroy(): void {
    this.resizeObserver?.disconnect();
    this.map?.remove();
  }

  protected setRadius(radius: number): void {
    this.radiusKm.set(radius);
    this.updateRadius();
  }

  protected toggleForage(): void {
    this.forageVisible.update(visible => !visible);
    this.updateForageLayer();
  }

  protected apiaryTitle(apiary: ApiaryMapMarker): string {
    return apiary.name?.trim() || apiary.stock_number;
  }

  private createMap(): void {
    this.map = this.leaflet!.map(this.mapContainer!.nativeElement, {
      center: [51.1657, 10.4515],
      zoom: 6,
      scrollWheelZoom: true
    });
    this.leaflet!.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap-Mitwirkende'
    }).addTo(this.map);
  }

  private loadData(): void {
    forkJoin({
      apiaries: this.mapService.getApiaryMarkers(),
      foragePlants: this.mapService.getForagePlants()
    }).subscribe({
      next: ({ apiaries, foragePlants }) => {
        this.markers = apiaries.filter(apiary => apiary.latitude !== null && apiary.longitude !== null);
        this.foragePlants = foragePlants;
        this.addApiaryMarkers();
        this.updateForageLayer();
        this.fitToMarkers();
        this.loading.set(false);
      },
      error: () => {
        this.loadError.set(this.translation.t('mapPage.error.load'));
        this.loading.set(false);
      }
    });
  }

  private addApiaryMarkers(): void {
    for (const apiary of this.markers) {
      const marker = this.leaflet!.marker([apiary.latitude!, apiary.longitude!], { icon: this.markerIcon() })
        .addTo(this.map!);
      marker.bindPopup(`<strong>${this.escapeHtml(this.apiaryTitle(apiary))}</strong><br>${apiary.hive_count} ${this.translation.t('mapPage.hives')}`);
      marker.on('click', () => {
        this.updateRadius([apiary.latitude!, apiary.longitude!]);
        this.loadWeather(apiary.id);
      });
    }
  }

  private loadWeather(apiaryId: number): void {
    this.selectedWeather.set(null);
    this.mapService.getApiaryWeather(apiaryId).subscribe({
      next: weather => this.selectedWeather.set(weather),
      error: () => this.selectedWeather.set(null)
    });
  }

  private updateRadius(center?: Leaflet.LatLngExpression): void {
    if (!this.map || !this.leaflet) return;
    const target = center ?? this.radiusCircle?.getLatLng() ?? this.map.getCenter();
    this.radiusCircle?.remove();
    this.radiusCircle = this.leaflet.circle(target, {
      radius: this.radiusKm() * 1000,
      color: '#2f6f5e',
      fillColor: '#2f6f5e',
      fillOpacity: 0.12
    }).addTo(this.map);
  }

  private updateForageLayer(): void {
    if (!this.map || !this.leaflet) return;
    this.forageLayer?.remove();
    if (!this.forageVisible()) return;
    this.forageLayer = this.leaflet.layerGroup();
    const month = new Date().getMonth() + 1;
    const activePlants = this.foragePlants.filter(plant => this.isBlooming(plant, month));
    for (const apiary of this.markers) {
      const popup = activePlants.length
        ? `<strong>${this.translation.t('mapPage.forageNow')}</strong><br>${activePlants.map(plant => this.escapeHtml(plant.name_de)).join(', ')}`
        : this.translation.t('mapPage.forageNone');
      this.leaflet.circleMarker([apiary.latitude!, apiary.longitude!], {
        radius: 8,
        color: '#d1a632',
        fillColor: '#f2c94c',
        fillOpacity: 0.75
      }).bindPopup(popup).addTo(this.forageLayer);
    }
    this.forageLayer.addTo(this.map);
  }

  private fitToMarkers(): void {
    if (!this.map || !this.markers.length || !this.leaflet) return;
    const bounds = this.leaflet.latLngBounds(this.markers.map(marker => [marker.latitude!, marker.longitude!]));
    this.map.fitBounds(bounds, { padding: [24, 24], maxZoom: 13 });
  }

  private isBlooming(plant: ForagePlantEntry, month: number): boolean {
    return plant.bloom_start_month <= plant.bloom_end_month
      ? month >= plant.bloom_start_month && month <= plant.bloom_end_month
      : month >= plant.bloom_start_month || month <= plant.bloom_end_month;
  }

  private markerIcon(): Leaflet.DivIcon {
    return this.leaflet!.divIcon({
      className: 'map-apiary-marker',
      html: '<span></span>',
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });
  }

  private escapeHtml(value: string): string {
    return value.replace(/[&<>'"]/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[character]!);
  }
}
