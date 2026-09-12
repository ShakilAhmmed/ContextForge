import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Provider } from "react-redux";
import { BrowserRouter } from "react-router-dom";
import { Toaster } from "sonner";

import App from "./App.tsx";
import { store } from "./app/store";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <App />
        <Toaster richColors position="top-right" closeButton />
      </BrowserRouter>
    </Provider>
  </StrictMode>,
);
