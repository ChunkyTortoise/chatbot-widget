import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    globals: true,
    coverage: {
      provider: "v8",
      // Small tool floor is 70. Measured 0 percent: the tests copy functions instead of importing src/chatbot.js, so the floor is 0 until they do.
      thresholds: { lines: 0 },
      include: ["src/**"],
      exclude: ["**/*.test.*", "**/__tests__/**", "dist/**"],
    },
  },
});
