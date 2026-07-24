import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import {
  FeedCalculatorRequest,
  FeedCalculatorResponse,
  HoneyPriceCalculatorRequest,
  HoneyPriceCalculatorResponse
} from '../models/calculators.models';

@Injectable({ providedIn: 'root' })
export class CalculatorsService {
  private readonly api = inject(ApiService);

  calculateFeed(payload: FeedCalculatorRequest): Observable<FeedCalculatorResponse> {
    return this.api.post<FeedCalculatorResponse>('/api/feed-calculator/calculate', payload);
  }

  calculateHoneyPrice(payload: HoneyPriceCalculatorRequest): Observable<HoneyPriceCalculatorResponse> {
    return this.api.post<HoneyPriceCalculatorResponse>('/api/honey-price-calculator/calculate', payload);
  }
}
