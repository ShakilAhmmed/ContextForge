export interface Citation {
  document_id: string;
  filename: string;
  chunk_text: string;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
}

export interface ChatRequest {
  question: string;
}
