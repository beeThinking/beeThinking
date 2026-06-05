import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  EventEmitter,
  Input,
  OnChanges,
  OnDestroy,
  Output,
  SimpleChanges,
  ViewChild,
  ChangeDetectorRef,
  inject
} from '@angular/core';

import type * as Leaflet from 'leaflet';

export interface ApiaryPosition {
  latitude: number;
  longitude: number;
}

@Component({
  selector: 'app-apiary-map-picker',
  templateUrl: './apiary-map-picker.component.html',
  styleUrl: './apiary-map-picker.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ApiaryMapPickerComponent implements AfterViewInit, OnChanges, OnDestroy {
  private readonly cdr = inject(ChangeDetectorRef);

  @Input() latitude: number | string | null | undefined = null;
  @Input() longitude: number | string | null | undefined = null;
  @Input() selectable = true;
  @Input() label = 'Standortkarte';

  @Output() positionChange = new EventEmitter<ApiaryPosition>();

  @ViewChild('mapContainer', { static: true }) private mapContainer?: ElementRef<HTMLDivElement>;

  private leaflet?: typeof Leaflet;
  private map?: Leaflet.Map;
  private marker?: Leaflet.Marker;
  private resizeObserver?: ResizeObserver;

  protected isReady = false;
  protected loadError = '';

  async ngAfterViewInit(): Promise<void> {
    try {
      const leafletModule = await import('leaflet');
      this.leaflet = (leafletModule.default ?? leafletModule) as typeof Leaflet;

      const position = this.currentPosition();
      const center: Leaflet.LatLngExpression = position ?? [51.1657, 10.4515];
      const zoom = position ? 14 : 6;

      this.map = this.leaflet.map(this.mapContainer!.nativeElement, {
        center,
        zoom,
        scrollWheelZoom: false,
        zoomControl: true
      });

      this.leaflet
        .tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 19,
          attribution: '&copy; OpenStreetMap-Mitwirkende'
        })
        .addTo(this.map);

      if (this.selectable) {
        this.map.on('click', event => this.setPosition(event.latlng.lat, event.latlng.lng, true));
      }

      if (position) {
        this.setPosition(position[0], position[1], false);
      }

      this.resizeObserver = new ResizeObserver(() => this.map?.invalidateSize());
      this.resizeObserver.observe(this.mapContainer!.nativeElement);
      this.isReady = true;
      this.cdr.markForCheck();
      [0, 100, 350].forEach(delay => setTimeout(() => this.map?.invalidateSize(), delay));
    } catch {
      this.loadError = 'Karte konnte nicht geladen werden.';
      this.cdr.markForCheck();
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (!this.map || !this.leaflet || (!changes['latitude'] && !changes['longitude'])) return;

    const position = this.currentPosition();
    if (position) {
      this.setPosition(position[0], position[1], false);
    }
  }

  ngOnDestroy(): void {
    this.resizeObserver?.disconnect();
    this.map?.remove();
  }

  protected useBrowserPosition(): void {
    if (!this.selectable || !navigator.geolocation) return;

    navigator.geolocation.getCurrentPosition(position => {
      this.setPosition(position.coords.latitude, position.coords.longitude, true);
      this.map?.setView([position.coords.latitude, position.coords.longitude], 15);
    });
  }

  private currentPosition(): [number, number] | null {
    const latitude = this.toNumber(this.latitude);
    const longitude = this.toNumber(this.longitude);
    if (latitude === null || longitude === null) return null;
    return [latitude, longitude];
  }

  private toNumber(value: number | string | null | undefined): number | null {
    if (value === null || value === undefined || value === '') return null;
    const parsed = typeof value === 'number' ? value : Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }

  private setPosition(latitude: number, longitude: number, emit: boolean): void {
    if (!this.map || !this.leaflet) return;

    const latLng: Leaflet.LatLngExpression = [latitude, longitude];
    if (!this.marker) {
      this.marker = this.leaflet.marker(latLng, { icon: this.markerIcon() }).addTo(this.map);
    } else {
      this.marker.setLatLng(latLng);
    }

    if (emit) {
      this.positionChange.emit({
        latitude: Number(latitude.toFixed(6)),
        longitude: Number(longitude.toFixed(6))
      });
    }
  }

  private markerIcon(): Leaflet.DivIcon {
    return this.leaflet!.divIcon({
      className: 'apiary-map-marker',
      html: '<span></span>',
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });
  }
}
