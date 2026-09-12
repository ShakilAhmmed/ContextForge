# ContextForge Frontend

React + TypeScript SPA (Vite) for the ContextForge API. Deployed as its own Docker image/stack, separate from the backend (`../ops/docker`) — talks to it over the network via CORS, not a shared compose network.

## Stack

- **Build**: Vite + TypeScript
- **State/data**: Redux Toolkit + RTK Query (`src/api/*Api.ts`, one file per backend resource, injected into a shared `baseApi`)
- **Forms**: `react-hook-form` + `zod` validation (`src/features/*/schema.ts`)
- **Styling**: Tailwind CSS v4, `lucide-react` icons, small CSS keyframe animations (`src/index.css`)
- **File upload**: `react-dropzone` (drag-and-drop), wired through `react-hook-form`'s `Controller`
- **Errors**: `sonner` toasts for every API/request failure (`api/errors.ts:reportError()`, called from each form's `catch`); field-level validation errors (required, invalid format) stay inline under the field with a red border via `FormField`
- **Routing**: `react-router-dom`

## Local development

```
npm install
cp .env.example .env   # VITE_API_BASE_URL, defaults to the backend's dev URL
npm run dev
```

Serves at `http://localhost:5173`. Requires the backend stack running (`../ops/docker`) — its `CORS_ALLOWED_ORIGINS` already includes `http://localhost:5173` by default.

## Docker (separate from the backend stack)

```
docker compose up --build
```

Serves the built static app via nginx at `http://localhost:8082` (`FRONTEND_PORT` in the environment to change). `VITE_API_BASE_URL` is baked in at build time (Vite env vars are compile-time, not runtime) — pass it as a build arg or env var before building if it differs from the default:

```
VITE_API_BASE_URL=https://api.example.com/api/v1 docker compose up --build
```

If you change the port, add the new origin to the backend's `CORS_ALLOWED_ORIGINS` (`ops/docker/.env`) and rebuild the `api` container — the browser calls the API cross-origin directly (no reverse proxy between frontend and backend), so CORS must allow whatever origin the frontend is actually served from.

## Project layout

```
src/
├── api/
│   ├── baseApi.ts       RTK Query base (fetchBaseQuery, auth header injection)
│   ├── <resource>Api.ts one per backend resource, injectEndpoints into baseApi
│   ├── errors.ts        RTK Query error -> message helpers
│   └── types/           one file per resource, mirrors app/schemas/ on the backend
├── app/
│   ├── store.ts         Redux store, localStorage persistence for auth
│   └── hooks.ts         typed useAppDispatch/useAppSelector
├── features/
│   ├── auth/            LoginPage, RegisterPage, authSlice, schema
│   ├── tenants/          CreateTenantPage, schema
│   └── documents/        DocumentsPage (polls for status), UploadDocumentForm, schema
├── components/           FormCard, FormField, SubmitButton (spinner on loading), Sidebar, AppLayout
└── routes/               ProtectedRoute (redirects to /login without a token)
```

## Notes

- JWT is persisted to `localStorage` (`contextforge.auth` key) so a page refresh doesn't log you out.
- `DocumentsPage` polls `GET /documents` every 4s — ingestion (chunk/PII-mask/embed/index) happens asynchronously in the backend's worker, so status (`queued` → `processing` → `indexed`/`failed`) updates without a manual refresh.
- Backend's self-signed dev cert (`https://contextforge.local:8443`) will show a browser warning on first cross-origin call unless you've already visited and accepted it, or you point `VITE_API_BASE_URL` at an HTTP/trusted endpoint.
