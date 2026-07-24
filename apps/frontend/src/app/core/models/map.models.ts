export interface ApiaryMapMarker {
  id: number;
  name: string | null;
  stock_number: string;
  latitude: number | null;
  longitude: number | null;
  hive_count: number;
}

export interface DailyForecast {
  date: string;
  weather_code: number | null;
  temperature_min: number | null;
  temperature_max: number | null;
  precipitation_sum: number | null;
}

export interface CurrentWeather {
  weather: string;
  weather_temperature: number | null;
  weather_humidity: number | null;
  weather_wind_speed: number | null;
  weather_precipitation: number | null;
  weather_code: number | null;
  weather_source: string;
  weather_fetched_at: string;
}

export interface ApiaryWeatherForecast {
  apiary_id: number;
  current: CurrentWeather | null;
  daily: DailyForecast[];
}

export interface ForagePlantEntry {
  id: string;
  name_de: string;
  name_latin: string | null;
  bloom_start_month: number;
  bloom_end_month: number;
  forage_value: string;
  notes: string | null;
}
