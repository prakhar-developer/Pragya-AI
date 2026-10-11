import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import "./index.css";
import App from "./App.tsx";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false },
  },
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            borderRadius: "12px",
            background: "#FFFFFF",
            color: "#1E293B",
            border: "1px solid #E2E8F0",
            fontSize: "14px",
          },
          success: { iconTheme: { primary: "#0F766E", secondary: "#FFFFFF" } },
          error: { iconTheme: { primary: "#9F1239", secondary: "#FFFFFF" } },
        }}
      />
    </QueryClientProvider>
  </StrictMode>
);
