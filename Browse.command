#!/bin/sh
# Opens this site's local link in the browser (Vite dev server). Run: ./browse
cd "$(dirname "$0")" || exit 1
[ -d node_modules ] || { echo "Installing dependencies (first run only)..."; npm install || exit 1; }
exec npx vite --open "$@"
