export type DocumentStatus = "queued" | "processing" | "indexed" | "failed";

export interface DocumentItem {
  id: string;
  tenant_id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  status: DocumentStatus;
  created_at: string;
}

export interface ChunkPoint {
  text: string;
  x: number;
  y: number;
}

export interface ListDocumentsParams {
  page?: number;
  page_size?: number;
  search?: string;
}
