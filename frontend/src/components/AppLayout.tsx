import type { ReactNode } from "react";

import { Sidebar } from "./Sidebar";

export function AppLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <main className="flex-1 overflow-y-auto px-8 py-8">
        <div className="mx-auto max-w-3xl">{children}</div>
      </main>
    </div>
  );
}
