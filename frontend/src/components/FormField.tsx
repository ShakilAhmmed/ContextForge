import type { InputHTMLAttributes } from "react";
import type { FieldError } from "react-hook-form";

type FormFieldProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  error?: FieldError;
};

export function FormField({ label, error, ...inputProps }: FormFieldProps) {
  return (
    <label className="mb-4 block">
      <span className="mb-1 block text-sm font-medium text-slate-700">{label}</span>
      <input
        {...inputProps}
        className={`w-full rounded-lg border px-3 py-2 text-sm outline-none transition-colors focus:ring-2 ${
          error
            ? "border-red-300 focus:border-red-500 focus:ring-red-100"
            : "border-slate-300 focus:border-indigo-500 focus:ring-indigo-100"
        }`}
      />
      {error && <span className="mt-1 block animate-fade-in text-sm text-red-600">{error.message}</span>}
    </label>
  );
}
