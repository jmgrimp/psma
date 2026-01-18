"use client";

import { useMemo, useState } from "react";

import { apiBaseUrl } from "@/lib/api";

type FetchState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; httpStatus: number; body: unknown }
  | { status: "error"; message: string; httpStatus?: number; body?: unknown };

function normalizeFetchError(err: unknown): { message: string; httpStatus?: number; body?: unknown } {
  if (typeof err === "object" && err !== null) {
    const maybe = err as { message?: unknown; httpStatus?: unknown; body?: unknown };
    const message = typeof maybe.message === "string" ? maybe.message : "Unknown error";
    const httpStatus = typeof maybe.httpStatus === "number" ? maybe.httpStatus : undefined;
    return { message, httpStatus, body: maybe.body };
  }
  if (err instanceof Error) return { message: err.message };
  return { message: "Unknown error" };
}

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

  const [availabilitySeriesId, setAvailabilitySeriesId] = useState("1396");
  const [availabilityCountry, setAvailabilityCountry] = useState("US");
  const [availabilityFacadeState, setAvailabilityFacadeState] = useState<FetchState>({ status: "idle" });

  const [tmdbProvidersListCountry, setTmdbProvidersListCountry] = useState("US");
  const [tmdbProvidersListLanguage, setTmdbProvidersListLanguage] = useState("en-US");
  const [tmdbProvidersListState, setTmdbProvidersListState] = useState<FetchState>({ status: "idle" });

  const [tmdbDiscoverProviderId, setTmdbDiscoverProviderId] = useState("8");
  const [tmdbDiscoverCountry, setTmdbDiscoverCountry] = useState("US");
  const [tmdbDiscoverMonetizationTypes, setTmdbDiscoverMonetizationTypes] = useState("flatrate");
  const [tmdbDiscoverSortBy, setTmdbDiscoverSortBy] = useState("popularity.desc");
  const [tmdbDiscoverPage, setTmdbDiscoverPage] = useState("1");
  const [tmdbDiscoverState, setTmdbDiscoverState] = useState<FetchState>({ status: "idle" });

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
              } catch (err: unknown) {
                const e = normalizeFetchError(err);
                setTvmazeSearchState({ status: "error", message: e.message, httpStatus: e.httpStatus, body: e.body });
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
              } catch (err: unknown) {
                const e = normalizeFetchError(err);
                setTvmazeShowState({ status: "error", message: e.message, httpStatus: e.httpStatus, body: e.body });
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
              } catch (err: unknown) {
                const e = normalizeFetchError(err);
                setTmdbSearchState({ status: "error", message: e.message, httpStatus: e.httpStatus, body: e.body });
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
              } catch (err: unknown) {
                const e = normalizeFetchError(err);
                setTmdbProvidersState({ status: "error", message: e.message, httpStatus: e.httpStatus, body: e.body });
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
        <h2 className="text-base font-medium">Availability: v1 façade (TMDB TV)</h2>

        <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-3">
          <input
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            value={availabilitySeriesId}
            onChange={(e) => setAvailabilitySeriesId(e.target.value)}
            placeholder="Series ID (e.g. 1396)"
          />
          <input
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            value={availabilityCountry}
            onChange={(e) => setAvailabilityCountry(e.target.value)}
            placeholder="Country (e.g. US)"
          />
          <button
            className="rounded-md border px-3 py-2 text-sm"
            onClick={async () => {
              setAvailabilityFacadeState({ status: "loading" });
              try {
                const country = availabilityCountry.trim();
                const url =
                  country.length > 0
                    ? `${baseUrl}/availability/v1/tmdb/tv/${encodeURIComponent(availabilitySeriesId)}?country=${encodeURIComponent(
                        country
                      )}`
                    : `${baseUrl}/availability/v1/tmdb/tv/${encodeURIComponent(availabilitySeriesId)}`;
                const result = await fetchJson(url);
                setAvailabilityFacadeState({ status: "success", ...result });
              } catch (err: unknown) {
                const e = normalizeFetchError(err);
                setAvailabilityFacadeState({ status: "error", message: e.message, httpStatus: e.httpStatus, body: e.body });
              }
            }}
          >
            Run
          </button>
        </div>

        {availabilityFacadeState.status === "loading" && (
          <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">Loading…</p>
        )}

        {availabilityFacadeState.status === "success" && (
          <>
            <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">HTTP {availabilityFacadeState.httpStatus}</p>
            <PrettyJson value={availabilityFacadeState.body} />
          </>
        )}

        {availabilityFacadeState.status === "error" && (
          <>
            <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">
              Error: {availabilityFacadeState.message}
              {availabilityFacadeState.httpStatus ? ` (HTTP ${availabilityFacadeState.httpStatus})` : ""}
            </p>
            {availabilityFacadeState.body !== undefined && <PrettyJson value={availabilityFacadeState.body} />}
          </>
        )}
      </section>

      <section className="rounded-md border p-4">
        <h2 className="text-base font-medium">TMDB: provider list (TV)</h2>

        <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-3">
          <input
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            value={tmdbProvidersListCountry}
            onChange={(e) => setTmdbProvidersListCountry(e.target.value)}
            placeholder="Country (e.g. US)"
          />
          <input
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            value={tmdbProvidersListLanguage}
            onChange={(e) => setTmdbProvidersListLanguage(e.target.value)}
            placeholder="Language (e.g. en-US)"
          />
          <button
            className="rounded-md border px-3 py-2 text-sm"
            onClick={async () => {
              setTmdbProvidersListState({ status: "loading" });
              try {
                const params = new URLSearchParams();
                const country = tmdbProvidersListCountry.trim();
                const language = tmdbProvidersListLanguage.trim();
                if (country.length > 0) params.set("country", country);
                if (language.length > 0) params.set("language", language);
                const url = `${baseUrl}/providers/tmdb/watch/providers/tv?${params.toString()}`;
                const result = await fetchJson(url);
                setTmdbProvidersListState({ status: "success", ...result });
              } catch (err: unknown) {
                const e = normalizeFetchError(err);
                setTmdbProvidersListState({ status: "error", message: e.message, httpStatus: e.httpStatus, body: e.body });
              }
            }}
          >
            Run
          </button>
        </div>

        {tmdbProvidersListState.status === "loading" && (
          <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">Loading…</p>
        )}

        {tmdbProvidersListState.status === "success" && (
          <>
            <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">
              HTTP {tmdbProvidersListState.httpStatus}
            </p>
            <PrettyJson value={tmdbProvidersListState.body} />
          </>
        )}

        {tmdbProvidersListState.status === "error" && (
          <>
            <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">
              Error: {tmdbProvidersListState.message}
              {tmdbProvidersListState.httpStatus ? ` (HTTP ${tmdbProvidersListState.httpStatus})` : ""}
            </p>
            {tmdbProvidersListState.body !== undefined && <PrettyJson value={tmdbProvidersListState.body} />}
          </>
        )}
      </section>

      <section className="rounded-md border p-4">
        <h2 className="text-base font-medium">TMDB: discover TV by provider</h2>

        <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-3">
          <input
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            value={tmdbDiscoverProviderId}
            onChange={(e) => setTmdbDiscoverProviderId(e.target.value)}
            placeholder="Provider ID (e.g. 8)"
          />
          <input
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            value={tmdbDiscoverCountry}
            onChange={(e) => setTmdbDiscoverCountry(e.target.value)}
            placeholder="Country (e.g. US)"
          />
          <input
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            value={tmdbDiscoverMonetizationTypes}
            onChange={(e) => setTmdbDiscoverMonetizationTypes(e.target.value)}
            placeholder="Monetization (e.g. flatrate,free)"
          />

          <input
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            value={tmdbDiscoverSortBy}
            onChange={(e) => setTmdbDiscoverSortBy(e.target.value)}
            placeholder="sort_by (e.g. popularity.desc)"
          />
          <input
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            value={tmdbDiscoverPage}
            onChange={(e) => setTmdbDiscoverPage(e.target.value)}
            placeholder="page (e.g. 1)"
          />
          <button
            className="rounded-md border px-3 py-2 text-sm"
            onClick={async () => {
              setTmdbDiscoverState({ status: "loading" });
              try {
                const params = new URLSearchParams();
                params.set("watch_provider_id", tmdbDiscoverProviderId.trim());

                const country = tmdbDiscoverCountry.trim();
                const monetization = tmdbDiscoverMonetizationTypes.trim();
                const sortBy = tmdbDiscoverSortBy.trim();
                const page = tmdbDiscoverPage.trim();

                if (country.length > 0) params.set("country", country);
                if (monetization.length > 0) params.set("monetization_types", monetization);
                if (sortBy.length > 0) params.set("sort_by", sortBy);
                if (page.length > 0) params.set("page", page);

                const url = `${baseUrl}/providers/tmdb/discover/tv?${params.toString()}`;
                const result = await fetchJson(url);
                setTmdbDiscoverState({ status: "success", ...result });
              } catch (err: unknown) {
                const e = normalizeFetchError(err);
                setTmdbDiscoverState({ status: "error", message: e.message, httpStatus: e.httpStatus, body: e.body });
              }
            }}
          >
            Run
          </button>
        </div>

        {tmdbDiscoverState.status === "loading" && (
          <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">Loading…</p>
        )}

        {tmdbDiscoverState.status === "success" && (
          <>
            <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">HTTP {tmdbDiscoverState.httpStatus}</p>
            <PrettyJson value={tmdbDiscoverState.body} />
          </>
        )}

        {tmdbDiscoverState.status === "error" && (
          <>
            <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">
              Error: {tmdbDiscoverState.message}
              {tmdbDiscoverState.httpStatus ? ` (HTTP ${tmdbDiscoverState.httpStatus})` : ""}
            </p>
            {tmdbDiscoverState.body !== undefined && <PrettyJson value={tmdbDiscoverState.body} />}
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
