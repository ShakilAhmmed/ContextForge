import { useState } from "react";

import { useUploadDocumentMutation } from "../../api/documentApi";
import { getErrorMessage } from "../../api/errors";

export type UploadStatus = "uploading" | "success" | "error";

export interface UploadItem {
  id: string;
  filename: string;
  status: UploadStatus;
  error?: string;
}

const AUTO_DISMISS_MS = 3000;

export function useUploadTray() {
  const [items, setItems] = useState<UploadItem[]>([]);
  const [uploadDocument] = useUploadDocumentMutation();

  function addFiles(files: File[]) {
    for (const file of files) {
      const id = `${file.name}-${crypto.randomUUID()}`;
      setItems((prev) => [...prev, { id, filename: file.name, status: "uploading" }]);

      uploadDocument(file)
        .unwrap()
        .then(() => {
          setItems((prev) => prev.map((i) => (i.id === id ? { ...i, status: "success" } : i)));
          setTimeout(() => setItems((prev) => prev.filter((i) => i.id !== id)), AUTO_DISMISS_MS);
        })
        .catch((err: unknown) => {
          setItems((prev) =>
            prev.map((i) => (i.id === id ? { ...i, status: "error", error: getErrorMessage(err) } : i)),
          );
        });
    }
  }

  function dismiss(id: string) {
    setItems((prev) => prev.filter((i) => i.id !== id));
  }

  return { items, addFiles, dismiss };
}
