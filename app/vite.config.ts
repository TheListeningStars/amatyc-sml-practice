import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

import { cloudflare } from "@cloudflare/vite-plugin";

// base "./" so the built site works from any path when self-hosted
export default defineConfig({ plugins: [react(), cloudflare()], base: "./" });