import { baseApi } from "./baseApi";
import type { ChatRequest, ChatResponse, SuccessResponse } from "./types";

export const chatApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    askQuestion: builder.mutation<ChatResponse, ChatRequest>({
      query: (body) => ({ url: "/chat/query", method: "POST", body }),
      transformResponse: (response: SuccessResponse<ChatResponse>) => response.data,
    }),
  }),
  overrideExisting: false,
});

export const { useAskQuestionMutation } = chatApi;
