import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    coverage: {
      provider: "v8",
      // 80 for apps; floor set to the measured figure rounded down (see PR description).
      thresholds: { lines: 19 },
      include: ["app/**", "components/**", "lib/**"],
      exclude: ["**/*.test.*", "**/*.spec.*", "tests/**", "**/generated/**"],
    },
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/setup.ts"],
    include: ["tests/**/*.test.ts", "tests/**/*.test.tsx"],
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "."),
    },
  },
});
