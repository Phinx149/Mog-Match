import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  workers: 1,
  timeout: 60000,
  use: { baseURL: "http://127.0.0.1:5174", trace: "retain-on-failure" },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"], channel: process.env.E2E_BROWSER_CHANNEL || "msedge" } }],
  webServer: [
    { command: process.platform === "win32" ? '"..\\backend\\.venv\\Scripts\\python.exe" ..\\backend\\tests\\chat_e2e_server.py' : "../backend/.venv/bin/python ../backend/tests/chat_e2e_server.py", url: "http://127.0.0.1:5002/api/health", timeout: 60000 },
    { command: "npm run dev -- --host 127.0.0.1 --port 5174 --strictPort", url: "http://127.0.0.1:5174", env: { VITE_API_URL: "http://127.0.0.1:5002" } },
  ],
});
