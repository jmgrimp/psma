"use client";

import { useMemo, useState } from "react";

import { apiBaseUrl } from "@/lib/api";

type FetchState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; httpStatus: number; body: unknown }
  | { status: "error"; message: string; httpStatus?: number; body?: unknown };

async function fetchJson(url: string): Promise<{ httpStatus: number; body: unknown }> {
  const res = await fetch(url, { cache: "no-store" });
  const httpStatus = res.status;

  let body: unknown;
  try {
    body = await res.json();
  } catch {
    body = await res.text();
  }

  if (!res.ok) {
    throw Object.assign(new Error(`Request failed: ${httpStatus}`), { httpStatus, body });
  }

  return { httpStatus, body };
}

function PrettyJson({ value }: { value: unknown }) {
  const text = useMemo(() => JSON.stringify(value, null, 2), [value]);
  return (
    <pre className="mt-3 overflow-auto rounded-md border bg-transparent p-3 text-xs">
      {text}
    </pre>
  );
}

export default function ProviderSmokePage() {
  const baseUrl = apiBaseUrl();

  const [tvmazeQuery, setTvmazeQuery] = useState("girls");
  const [tvmazeSearchState, setTvmazeSearchState] = useState<FetchState>({ status: "idle" });

  const [tvmazeShowId, setTvmazeShowId] = useState("1");
  const [tvmazeEmbed, setTvmazeEmbed] = useState("episodes");
  const [tvmazeShowState, setTvmazeShowState] = useState<FetchState>({ status: "idle" });

  const [tmdbQuery, setTmdbQuery] = useState("Breaking Bad");
  const [tmdbSearchState, setTmdbSearchState] = useState<FetchState>({ status: "idle" });

  const [tmdbSeriesId, setTmdbSeriesId] = useState("1396");
  const [tmdbCountry, setTmdbCountry] = useState("US");
  const [tmdbProvidersState, setTmdbProvidersState] = useState<FetchState>({ status: "idle" });

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col gap-6 p-10">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl font-semibold tracking-tight">Provider smoke tests</h1>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Runs real calls via the PSMA API (no keys in the browser).
        </p>
        <p className="text-xs text-zinc-600 dark:text-zinc-400">
          API base URL: <span className="font-mono">{baseUrl}</span>
        </p>
      </header>

      <section className="rounded-md border p-4">
        <h2 className="text-base font-medium">TVmaze: show search</h2>

        <div className="mt-3 flex gap-2">
          <input
            className="w-full rounded-md border bg-transparent px-3 py-2 text-sm"
            value={tvmazeQuery}
            onChange={(e) => setTvmazeQuery(e.target.value)}
            placeholder="Query (e.g. girls)"
          />
          <button
            className="rounded-md border px-3 py-2 text-sm"
            onClick={async () => {
              setTvmazeSearchState({ status: "loading" });
              try {
                const url = `${baseUrl}/providers/tvmaze/search/shows?q=${encodeURIComponent(tvmazeQuery)}`;
                const result = await fetchJson(url);
                setTvmazeSearchState({ status: "success", ...result });
              } catch (err: any) {
                setTvmazeSearchState({
                  status: "error",
                  message: err?.message ?? "Unknown error",
                  httpStatus: err?.httpStatus,
                  body: err?.body,
                });
              }
            }}
          >
            Run
          </button>
        </div>

        {tvmazeSearchState.status === "loading" && (
          <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">Loading…</p>
        )}

        {tvmazeSearchState.status === "success" && (
          <>
            <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">
              HTTP {tvmazeSearchState.httpStatus}
            </p>
            <PrettyJson value={tvmazeSearchState.body} />
          </>
        )}

        {tvmazeSearchState.status === "error" && (
          <>
            <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">
              Error: {tvmazeSearchState.message}
              {tvmazeSearchState.httpStatus ? ` (HTTP ${tvmazeSearchState.httpStatus})` : ""}
            </p>
            {tvmazeSearchState.body !== undefined && <PrettyJson value={tvmazeSearchState.body} />}
          </>
        )}
      </section>

      <section className="rounded-md border p-4">
        <h2 className="text-base font-medium">TVmaze: show details</h2>

        <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-3">
          <input
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            value={tvmazeShowId}
            onChange={(e) => setTvmazeShowId(e.target.value)}
            placeholder="Show ID (e.g. 1)"
          />
          <input
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            value={tvmazeEmbed}
            onChange={(e) => setTvmazeEmbed(e.target.value)}
            placeholder="embed (e.g. episodes)"
          />
          <button
            className="rounded-md border px-3 py-2 text-sm"
            onClick={async () => {
              setTvmazeShowState({ status: "loading" });
              try {
                const embed = tvmazeEmbed.trim();
                const url =
                  embed.length > 0
                    ? `${baseUrl}/providers/tvmaze/shows/${encodeURIComponent(tvmazeShowId)}?embed=${encodeURIComponent(embed)}`
                    : `${baseUrl}/providers/tvmaze/shows/${encodeURIComponent(tvmazeShowId)}`;

                const result = await fetchJson(url);
                setTvmazeShowState({ status: "success", ...result });
              } catch (err: any) {
                setTvmazeShowState({
                  status: "error",
                  message: err?.message ?? "Unknown error",
                  httpStatus: err?.httpStatus,
                  body: err?.body,
                });
              }
            }}
          >
            Run
          </button>
        </div>

        {tvmazeShowState.status === "loading" && (
          <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">Loading…</p>
        )}

        {tvmazeShowState.status === "success" && (
          <>
            <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">HTTP {tvmazeShowState.httpStatus}</p>
            <PrettyJson value={tvmazeShowState.body} />
          </>
        )}

        {tvmazeShowState.status === "error" && (
          <>
            <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">
              Error: {tvmazeShowState.message}
              {tvmazeShowState.httpStatus ? ` (HTTP ${tvmazeShowState.httpStatus})` : ""}
            </p>
            {tvmazeShowState.body !== undefined && <PrettyJson value={tvmazeShowState.body} />}
          </>
        )}
      </section>

      <section className="rounded-md border p-4">
        <h2 className="text-base font-medium">TMDB: search TV</h2>

        <div className="mt-3 flex gap-2">
          <input
            className="w-full rounded-md border bg-transparent px-3 py-2 text-sm"
            value={tmdbQuery}
            onChange={(e) => setTmdbQuery(e.target.value)}
            placeholder="Query (e.g. Breaking Bad)"
          />
          <button
            className="rounded-md border px-3 py-2 text-sm"
            onClick={async () => {
              setTmdbSearchState({ status: "loading" });
              try {
                const url = `${baseUrl}/providers/tmdb/search/tv?query=${encodeURIComponent(tmdbQuery)}`;
                const result = await fetchJson(url);
                setTmdbSearchState({ status: "success", ...result });
              } catch (err: any) {
                setTmdbSearchState({
                  status: "error",
                  message: err?.message ?? "Unknown error",
                  httpStatus: err?.httpStatus,
                  body: err?.body,
                });
              }
            }}
          >
            Run
          </button>
        </div>

        {tmdbSearchState.status === "loading" && (
          <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">Loading…</p>
        )}

        {tmdbSearchState.status === "success" && (
          <>
            <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">HTTP {tmdbSearchState.httpStatus}</p>
            <PrettyJson value={tmdbSearchState.body} />
          </>
        )}

        {tmdbSearchState.status === "error" && (
          <>
            <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">
              Error: {tmdbSearchState.message}
              {tmdbSearchState.httpStatus ? ` (HTTP ${tmdbSearchState.httpStatus})` : ""}
            </p>
            {tmdbSearchState.body !== undefined && <PrettyJson value={tmdbSearchState.body} />}
          </>
        )}
      </section>

      <section className="rounded-md border p-4">
        <h2 className="text-base font-medium">TMDB: watch providers</h2>

        <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-3">
          <input
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            value={tmdbSeriesId}
            onChange={(e) => setTmdbSeriesId(e.target.value)}
            placeholder="Series ID (e.g. 1396)"
          />
          <input
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            value={tmdbCountry}
            onChange={(e) => setTmdbCountry(e.target.value)}
            placeholder="Country (e.g. US)"
          />
          <button
            className="rounded-md border px-3 py-2 text-sm"
            onClick={async () => {
              setTmdbProvidersState({ status: "loading" });
              try {
                const country = tmdbCountry.trim();
                const url =
                  country.length > 0
                    ? `${baseUrl}/providers/tmdb/tv/${encodeURIComponent(tmdbSeriesId)}/watch/providers?country=${encodeURIComponent(country)}`
                    : `${baseUrl}/providers/tmdb/tv/${encodeURIComponent(tmdbSeriesId)}/watch/providers`;

                const result = await fetchJson(url);
                setTmdbProvidersState({ status: "success", ...result });
              } catch (err: any) {
                setTmdbProvidersState({
                  status: "error",
                  message: err?.message ?? "Unknown error",
                  httpStatus: err?.httpStatus,
                  body: err?.body,
                });
              }
            }}
          >
            Run
          </button>
        </div>

        {tmdbProvidersState.status === "loading" && (
          <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">Loading…</p>
        )}

        {tmdbProvidersState.status === "success" && (
          <>
            <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">
              HTTP {tmdbProvidersState.httpStatus}
            </p>
            <PrettyJson value={tmdbProvidersState.body} />
          </>
        )}

        {tmdbProvidersState.status === "error" && (
          <>
            <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">
              Error: {tmdbProvidersState.message}
              {tmdbProvidersState.httpStatus ? ` (HTTP ${tmdbProvidersState.httpStatus})` : ""}
            </p>
            {tmdbProvidersState.body !== undefined && <PrettyJson value={tmdbProvidersState.body} />}
          </>
        )}
      </section>

      <section className="rounded-md border p-4">
        <h2 className="text-base font-medium">Notes</h2>
        <ul className="mt-2 list-disc pl-5 text-sm text-zinc-600 dark:text-zinc-400">
          <li>
            TMDB endpoints will return HTTP 503 until the API is configured with <span className="font-mono">PSMA_TMDB_API_KEY</span>.
          </li>
          <li>
            Responses include an <span className="font-mono">attribution</span> field when required (TVmaze, and TMDB watch providers).
          </li>
        </ul>
      </section>
    </main>
  );
}
