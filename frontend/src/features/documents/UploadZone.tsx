import { Dropzone } from "./Dropzone";
import { UploadTray } from "./UploadTray";
import { useUploadTray } from "./useUploadTray";

export function UploadZone() {
  const { items, addFiles, dismiss } = useUploadTray();

  return (
    <>
      <div className="mb-8 animate-fade-in-up rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h2 className="mb-4 text-sm font-semibold text-slate-900">Upload documents</h2>
        <Dropzone onFiles={addFiles} />
      </div>
      <UploadTray items={items} onDismiss={dismiss} />
    </>
  );
}
