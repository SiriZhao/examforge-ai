/// <reference types="vitest" />

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const repoName = process.env.GITHUB_REPOSITORY?.split("/")[1];
const isUserSite = repoName?.endsWith(".github.io");
const base = process.env.VITE_APP_BASE_PATH || (isUserSite ? "/" : repoName ? `/${repoName}/` : "/");

export default defineConfig({
  base,
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
  },
});
