export interface SuccessResponse<T> {
  success: true;
  code: number;
  message: string | null;
  data: T;
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface PaginatedResponse<T> {
  success: true;
  code: number;
  message: string | null;
  data: T[];
  meta: PaginationMeta;
}

export interface ErrorDetail {
  field: string | null;
  message: string;
}

export interface ErrorResponse {
  success: false;
  code: number;
  error: {
    type: string;
    message: string;
    details: ErrorDetail[];
  };
}
