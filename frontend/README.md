# Browser HTML Capture Extension

Vue 3 + TypeScript + Tailwind popup for a Chrome/Edge Manifest V3 extension.

## What it does

Click the button in the popup and the extension reads the active tab's HTML, then POSTs it to the configured API.

## Setup

1. Install dependencies with your package manager.
2. Set `VITE_API_URL` to `http://127.0.0.1:8000/capture` if you want to override the default.
3. Keep `public/manifest.json` pointed at localhost if you change the backend port.
4. Run `npm run build` and load the `dist` folder as an unpacked extension.

## Notes

The popup uses `chrome.scripting.executeScript` plus `chrome.tabs.query`, so the extension needs `activeTab` and `scripting` permissions.