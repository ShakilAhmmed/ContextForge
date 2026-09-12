import { baseApi } from "./baseApi";
import type {
  ChunkPoint,
  DocumentItem,
  ListDocumentsParams,
  PaginatedResponse,
  SuccessResponse,
} from "./types";

export const documentApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    uploadDocument: builder.mutation<DocumentItem, File>({
      query: (file) => {
        const formData = new FormData();
        formData.append("file", file);
        return { url: "/documents", method: "POST", body: formData };
      },
      transformResponse: (response: SuccessResponse<DocumentItem>) => response.data,
      invalidatesTags: ["Document"],
    }),

    listDocuments: builder.query<PaginatedResponse<DocumentItem>, ListDocumentsParams | void>({
      query: (params) => ({ url: "/documents", params: params ?? undefined }),
      providesTags: ["Document"],
    }),

    getDocument: builder.query<DocumentItem, string>({
      query: (id) => `/documents/${id}`,
      transformResponse: (response: SuccessResponse<DocumentItem>) => response.data,
      providesTags: ["Document"],
    }),

    getDocumentChunks: builder.query<ChunkPoint[], string>({
      query: (id) => `/documents/${id}/chunks`,
      transformResponse: (response: SuccessResponse<ChunkPoint[]>) => response.data,
    }),
  }),
  overrideExisting: false,
});

export const {
  useUploadDocumentMutation,
  useListDocumentsQuery,
  useGetDocumentQuery,
  useGetDocumentChunksQuery,
} = documentApi;
