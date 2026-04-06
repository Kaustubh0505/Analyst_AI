import { reactRouter } from "@react-router/dev/vite";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";
import type { Plugin } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";

// Silences the Chrome DevTools .well-known request so React Router doesn't
// throw "No route matches URL" errors in the dev console.
function ignoreDevToolsPlugin(): Plugin {
  return {
    name: "ignore-chrome-devtools-json",
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        if (req.url === "/.well-known/appspecific/com.chrome.devtools.json") {
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end("{}");
          return;
        }
        next();
      });
    },
  };
}

export default defineConfig({
  plugins: [tailwindcss(), ignoreDevToolsPlugin(), reactRouter(), tsconfigPaths()],
});
