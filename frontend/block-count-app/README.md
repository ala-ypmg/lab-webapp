# YPB Daily Block Count App

React + TypeScript frontend for logging YPB (Yellow Pathology Block) daily block counts. Used by the **Checkout** department as Page 2 of the lab workflow.

## Overview

This app is embedded into the Lab Workflow Webapp. It captures daily block count data per cassette type, which is stored in the workflow session and included in the final form submission.

## Development

```bash
cd frontend/ypb-daily-count
npm install
npm run dev      # Dev server at http://localhost:5173
npm run build    # Production build → dist/
```

## Production Build

After building, copy the compiled assets into Flask's static directory so they are served by the backend:

```bash
npm run build
cp -r dist/assets ../../static/assets
```

The Flask template `templates/ypb_daily_count.html` references these built assets.

## Stack

| Tool | Purpose |
|------|---------|
| React 18 | UI framework |
| TypeScript | Type safety |
| Vite | Build tool / dev server |
| ESLint | Linting |
