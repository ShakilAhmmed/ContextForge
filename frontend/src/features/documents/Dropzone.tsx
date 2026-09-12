import { UploadCloud } from "lucide-react";
import { useCallback } from "react";
import { useDropzone } from "react-dropzone";

const ACCEPT = {
  "application/pdf": [".pdf"],
  "text/plain": [".txt"],
  "text/markdown": [".md"],
};

export function Dropzone({ onFiles }: { onFiles: (files: File[]) => void }) {
  const onDrop = useCallback(
    (accepted: File[]) => {
      if (accepted.length) onFiles(accepted);
    },
    [onFiles],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPT,
    multiple: true,
  });

  return (
    <div
      {...getRootProps()}
      className={`group flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed px-6 py-10 text-center transition-all duration-200 ${
        isDragActive
          ? "scale-[1.01] border-indigo-500 bg-indigo-50"
          : "border-slate-300 bg-slate-50 hover:border-indigo-400 hover:bg-indigo-50/50"
      }`}
    >
      <input {...getInputProps()} />
      <UploadCloud
        className={`size-8 text-slate-400 transition-transform duration-200 ${
          isDragActive ? "-translate-y-1 text-indigo-500" : "group-hover:-translate-y-0.5"
        }`}
      />
      <p className="text-sm font-medium text-slate-700">
        {isDragActive ? "Drop to upload" : "Drag & drop files, or click to browse"}
      </p>
      <p className="text-xs text-slate-400">PDF, TXT, or Markdown · multiple files supported</p>
    </div>
  );
}
