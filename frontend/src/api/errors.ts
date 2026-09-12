import { toast } from "sonner";

import type { ErrorResponse } from "./types";

export function isErrorResponse(error: unknown): error is { data: ErrorResponse } {
  return (
    typeof error === "object" &&
    error !== null &&
    "data" in error &&
    typeof (error as { data?: unknown }).data === "object"
  );
}

export function getErrorMessage(error: unknown): string {
  if (isErrorResponse(error)) return error.data.error?.message ?? "Request failed";
  return "Request failed";
}

/** Every request failure surfaces as a toast - no inline error text in forms. */
export function reportError(error: unknown): void {
  toast.error(getErrorMessage(error));
}
