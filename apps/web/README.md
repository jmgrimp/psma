# PSMA Web (Next.js)

## Prereqs

- Node.js >= 20.9 (recommended: use repo root `.nvmrc`)
- pnpm (via Corepack)

## Install

From repo root:

- `pnpm install`

## Run (dev)

In two terminals from repo root:

- `pnpm dev:api`
- `pnpm dev:web`

Web runs on `http://localhost:3000`.

## Environment

- Copy `.env.local.example` → `.env.local`
- Set `NEXT_PUBLIC_API_BASE_URL` (default: `http://localhost:8000`)
