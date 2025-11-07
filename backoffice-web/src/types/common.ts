// Common types used across the application

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  detail: string;
  status_code?: number;
}

export interface SuccessResponse {
  message: string;
  data?: any;
}

export type SortOrder = 'asc' | 'desc';

export interface PaginationParams {
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: SortOrder;
}

export interface DateRange {
  start_date?: string;
  end_date?: string;
}
