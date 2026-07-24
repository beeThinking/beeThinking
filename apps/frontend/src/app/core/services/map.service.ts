import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { ApiaryMapMarker, ApiaryWeatherForecast, ForagePlantEntry } from '../models/map.models';

@Injectable({ providedIn: 'root' })
export class MapService {
  private readonly api = inject(ApiService);

  getApiaryMarkers(): Observable<ApiaryMapMarker[]> {
    return this.api.get<ApiaryMapMarker[]>('/api/map/apiaries');
  }

  getApiaryWeather(apiaryId: number, forecastDays = 3): Observable<ApiaryWeatherForecast> {
    return this.api.get<ApiaryWeatherForecast>(`/api/map/apiaries/${apiaryId}/weather?forecast_days=${forecastDays}`);
  }

  getForagePlants(): Observable<ForagePlantEntry[]> {
    return this.api.get<ForagePlantEntry[]>('/api/map/forage-plants');
  }
}
