"use client";

import { useEffect, useMemo, useState } from "react";

import { apiBaseUrl } from "@/lib/api";

type FetchState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; httpStatus: number; body: T }
  | { status: "error"; message: string; httpStatus?: number; body?: unknown };

type ProviderEnvelope<T> = {
  provider: string;
  retrieved_at: string;
  attribution: null | { required: boolean; text: string; url?: string | null };
  request: Record<string, unknown>;
  data: T;
};

type TmdbGenreListResponse = {
  genres?: Array<{ id: number; name: string }>;
};

type TmdbDiscoverTvResponse = {
  page?: number;
  results?: Array<{ id: number; name?: string; original_name?: string; first_air_date?: string }>;
};

type AvailabilityNowV1 = "true" | "false" | "unknown";
type ProviderCategoryV1 = "svod" | "avod" | "tvod" | "live_bundle" | "unknown";
type ConfidenceV1 = "high" | "medium" | "low";

type AvailabilityAssessmentV1 = {
  title_id: string;
  country: string;
  service_id: string;
  provider_category: ProviderCategoryV1;
  availability_now: AvailabilityNowV1;
  confidence: ConfidenceV1;
  reason_codes: string[];
  evidence: unknown[];
};

type AvailabilityAssessmentsResponseV1 = {
  retrieved_at: string;
  assessments: AvailabilityAssessmentV1[];
};

type PlanEventV1 = {
  action: "subscribe" | "unsubscribe";
  service_id: string;
  effective_at: string;
  reason_codes: string[];
  title_ids: string[];
  assumptions?: string[];
};

type PlanResponseV1 = {
  generated_at: string;
  country: string;
  horizon_days: number;
  events: PlanEventV1[];
  questions?: Array<{
    id: string;
    key: string;
    prompt: string;
    required: boolean;
    service_id?: string | null;
    title_ids?: string[] | null;
    answer_schema?: Record<string, unknown> | null;
    rationale?: string | null;
  }>;
};

type TvmazeSearchResult = Array<{ score: number; show: { id: number; name: string } }>;

type TvmazeShowWithEpisodes = {
  id: number;
  name?: string;
  _embedded?: {
    episodes?: Array<{
      id: number;
      name?: string;
      season?: number;
      number?: number;
      airstamp?: string | null;
      airdate?: string | null;
      airtime?: string | null;
    }>;
  };
};

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

async function fetchJson<T>(url: string): Promise<{ httpStatus: number; body: T }> {
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

  return { httpStatus, body: body as T };
}

async function fetchJsonWithInit<T>(url: string, init: RequestInit): Promise<{ httpStatus: number; body: T }> {
  const res = await fetch(url, { cache: "no-store", ...init });
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

  return { httpStatus, body: body as T };
}

function PrettyJson({ value }: { value: unknown }) {
  const text = useMemo(() => JSON.stringify(value, null, 2), [value]);
  return (
    <pre className="mt-3 overflow-auto rounded-md border bg-transparent p-3 text-xs">
      {text}
    </pre>
  );
}

function formatEpisodeTime(e: { airstamp?: string | null; airdate?: string | null; airtime?: string | null }): string {
  if (e.airstamp) {
    const d = new Date(e.airstamp);
    if (!Number.isNaN(d.getTime())) {
      return d.toLocaleString();
    }
  }

  if (e.airdate && e.airtime) return `${e.airdate} ${e.airtime}`;
  if (e.airdate) return `${e.airdate}`;
  return "(unknown)";
}

function parseEpisodeTimestamp(e: { airstamp?: string | null; airdate?: string | null; airtime?: string | null }): number {
  if (e.airstamp) {
    const ts = Date.parse(e.airstamp);
    if (!Number.isNaN(ts)) return ts;
  }

  // Best-effort fallback when airstamp is missing.
  if (e.airdate && e.airtime) {
    const ts = Date.parse(`${e.airdate}T${e.airtime}`);
    if (!Number.isNaN(ts)) return ts;
  }

  if (e.airdate) {
    const ts = Date.parse(e.airdate);
    if (!Number.isNaN(ts)) return ts;
  }

  return Number.NaN;
}

function extractEpisodeAirTimes(
  show: TvmazeShowWithEpisodes | null,
  maxUpcoming = 5,
  maxPast = 5
): { upcoming: string[]; past: string[]; nextAir?: string; lastAir?: string } {
  const episodes = show?._embedded?.episodes ?? [];
  if (episodes.length === 0) return { upcoming: [], past: [] };

  const now = Date.now();
  const withTs = episodes
    .map((e) => ({ e, ts: parseEpisodeTimestamp(e) }))
    .filter(({ ts }) => !Number.isNaN(ts));

  const upcomingSorted = withTs
    .filter(({ ts }) => ts >= now)
    .sort((a, b) => a.ts - b.ts);
  const pastSorted = withTs
    .filter(({ ts }) => ts < now)
    .sort((a, b) => b.ts - a.ts);

  const upcoming = upcomingSorted.slice(0, maxUpcoming).map(({ e }) => formatEpisodeTime(e));
  const past = pastSorted.slice(0, maxPast).map(({ e }) => formatEpisodeTime(e));

  const nextAir = upcomingSorted.length > 0 ? new Date(upcomingSorted[0].ts).toLocaleString() : undefined;
  const lastAir = pastSorted.length > 0 ? new Date(pastSorted[0].ts).toLocaleString() : undefined;

  return { upcoming, past, nextAir, lastAir };
}

export default function InteractiveSmokePage() {
  const baseUrl = apiBaseUrl();

  const [country, setCountry] = useState("US");

  const [permanentServiceIdsText, setPermanentServiceIdsText] = useState("youtube_tv");
  const [horizonDaysText, setHorizonDaysText] = useState("30");

  // 1) Genres
  const [genresState, setGenresState] = useState<FetchState<ProviderEnvelope<TmdbGenreListResponse>>>({
    status: "idle",
  });
  const [selectedGenre, setSelectedGenre] = useState<{ id: number; name: string } | null>(null);

  // 2) Shows by genre
  const [showsState, setShowsState] = useState<FetchState<ProviderEnvelope<TmdbDiscoverTvResponse>>>({
    status: "idle",
  });
  const [selectedShow, setSelectedShow] = useState<{ tmdbId: number; name: string } | null>(null);

  // 3) Availability (stable API façade)
  const [availabilityState, setAvailabilityState] = useState<FetchState<AvailabilityAssessmentsResponseV1>>(
    { status: "idle" }
  );
  const [selectedService, setSelectedService] = useState<Pick<
    AvailabilityAssessmentV1,
    "service_id" | "provider_category" | "availability_now" | "confidence"
  > | null>(null);

  // 4) Dates/times (loaded after provider click)
  const [episodesState, setEpisodesState] = useState<FetchState<ProviderEnvelope<TvmazeShowWithEpisodes>>>(
    { status: "idle" }
  );

  const [planState, setPlanState] = useState<FetchState<PlanResponseV1>>({ status: "idle" });

  useEffect(() => {
    // Load genres once.
    if (genresState.status !== "idle") return;
    (async () => {
      setGenresState({ status: "loading" });
      try {
        const url = `${baseUrl}/providers/tmdb/genre/tv/list?language=en-US`;
        const result = await fetchJson<ProviderEnvelope<TmdbGenreListResponse>>(url);
        setGenresState({ status: "success", ...result });
      } catch (err: unknown) {
        const e = normalizeFetchError(err);
        setGenresState({ status: "error", message: e.message, httpStatus: e.httpStatus, body: e.body });
      }
    })();
  }, [baseUrl, genresState.status]);

  useEffect(() => {
    // Reset downstream state when genre changes.
    setShowsState({ status: "idle" });
    setSelectedShow(null);
    setAvailabilityState({ status: "idle" });
    setSelectedService(null);
    setEpisodesState({ status: "idle" });
    setPlanState({ status: "idle" });
  }, [selectedGenre?.id]);

  useEffect(() => {
    if (!selectedGenre) return;

    (async () => {
      setShowsState({ status: "loading" });
      try {
        const params = new URLSearchParams();
        params.set("genre_id", String(selectedGenre.id));
        params.set("sort_by", "popularity.desc");
        params.set("page", "1");
        const url = `${baseUrl}/providers/tmdb/discover/tv/by-genre?${params.toString()}`;
        const result = await fetchJson<ProviderEnvelope<TmdbDiscoverTvResponse>>(url);
        setShowsState({ status: "success", ...result });
      } catch (err: unknown) {
        const e = normalizeFetchError(err);
        setShowsState({ status: "error", message: e.message, httpStatus: e.httpStatus, body: e.body });
      }
    })();
  }, [baseUrl, selectedGenre]);

  useEffect(() => {
    // Reset downstream state when show changes.
    setAvailabilityState({ status: "idle" });
    setSelectedService(null);
    setEpisodesState({ status: "idle" });
    setPlanState({ status: "idle" });
  }, [selectedShow?.tmdbId]);

  useEffect(() => {
    if (!selectedShow) return;

    (async () => {
      setAvailabilityState({ status: "loading" });
      setSelectedService(null);
      setEpisodesState({ status: "idle" });
      setPlanState({ status: "idle" });
      try {
        const url = `${baseUrl}/availability/v1/tmdb/tv/${encodeURIComponent(
          String(selectedShow.tmdbId)
        )}?country=${encodeURIComponent(country.trim() || "US")}`;
        const result = await fetchJson<AvailabilityAssessmentsResponseV1>(url);
        setAvailabilityState({ status: "success", ...result });
      } catch (err: unknown) {
        const e = normalizeFetchError(err);
        setAvailabilityState({ status: "error", message: e.message, httpStatus: e.httpStatus, body: e.body });
      }
    })();
  }, [baseUrl, country, selectedShow]);

  const episodeAirTimes = useMemo(() => {
    if (episodesState.status !== "success") return { upcoming: [], past: [] as string[] };
    return extractEpisodeAirTimes(episodesState.body.data, 5, 5);
  }, [episodesState]);

  const serviceList = useMemo(() => {
    if (availabilityState.status !== "success") return [] as AvailabilityAssessmentV1[];
    return availabilityState.body.assessments ?? [];
  }, [availabilityState]);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col gap-6 p-10">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl font-semibold tracking-tight">Interactive service tester</h1>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Genre → Shows → Providers → Dates/times (TVmaze episodes)
        </p>
        <p className="text-xs text-zinc-600 dark:text-zinc-400">
          API base URL: <span className="font-mono">{baseUrl}</span>
        </p>
      </header>

      <section className="rounded-md border p-4">
        <h2 className="text-base font-medium">Settings</h2>
        <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-3">
          <input
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            value={country}
            onChange={(e) => setCountry(e.target.value)}
            placeholder="Country (e.g. US)"
          />
          <input
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            value={permanentServiceIdsText}
            onChange={(e) => setPermanentServiceIdsText(e.target.value)}
            placeholder="Permanent services (comma-separated service_id)"
          />
          <input
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            value={horizonDaysText}
            onChange={(e) => setHorizonDaysText(e.target.value)}
            placeholder="Plan horizon days (e.g. 30)"
          />
        </div>
      </section>

      <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="rounded-md border p-4">
          <h2 className="text-base font-medium">1) Genres</h2>

          {genresState.status === "loading" && (
            <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">Loading…</p>
          )}
          {genresState.status === "error" && (
            <>
              <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">
                Error: {genresState.message}
                {genresState.httpStatus ? ` (HTTP ${genresState.httpStatus})` : ""}
              </p>
              {genresState.body !== undefined && <PrettyJson value={genresState.body} />}
            </>
          )}

          <div className="mt-3 flex flex-col gap-2">
            {(genresState.status === "success" ? genresState.body.data.genres ?? [] : []).map((g) => {
              const isSelected = selectedGenre?.id === g.id;
              return (
                <button
                  key={g.id}
                  className={`rounded-md border px-3 py-2 text-left text-sm ${
                    isSelected ? "bg-zinc-50 dark:bg-zinc-900" : "bg-transparent"
                  }`}
                  onClick={() => setSelectedGenre({ id: g.id, name: g.name })}
                >
                  {g.name}
                </button>
              );
            })}

            {genresState.status === "success" && (genresState.body.data.genres ?? []).length === 0 && (
              <p className="text-sm text-zinc-600 dark:text-zinc-400">No genres returned.</p>
            )}
          </div>
        </div>

        <div className="rounded-md border p-4">
          <h2 className="text-base font-medium">2) Shows</h2>

          {!selectedGenre ? (
            <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">Select a genre.</p>
          ) : (
            <>
              <div className="mt-2 flex items-center justify-between gap-3">
                <div className="text-sm text-zinc-600 dark:text-zinc-400">
                  Selected: <span className="font-medium text-zinc-900 dark:text-zinc-100">{selectedGenre.name}</span>
                </div>
                <div className="text-xs text-zinc-600 dark:text-zinc-400">Top 20 (TMDB page 1)</div>
              </div>

              {showsState.status === "loading" && (
                <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">Loading…</p>
              )}
              {showsState.status === "error" && (
                <>
                  <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">
                    Error: {showsState.message}
                    {showsState.httpStatus ? ` (HTTP ${showsState.httpStatus})` : ""}
                  </p>
                  {showsState.body !== undefined && <PrettyJson value={showsState.body} />}
                </>
              )}

              <div className="mt-3 flex flex-col gap-2">
                {(showsState.status === "success" ? showsState.body.data.results ?? [] : []).map((s) => {
                  const name = s.name ?? s.original_name ?? `TMDB ${s.id}`;
                  const isSelected = selectedShow?.tmdbId === s.id;
                  return (
                    <button
                      key={s.id}
                      className={`rounded-md border px-3 py-2 text-left text-sm ${
                        isSelected ? "bg-zinc-50 dark:bg-zinc-900" : "bg-transparent"
                      }`}
                      onClick={() => setSelectedShow({ tmdbId: s.id, name })}
                    >
                      <div className="truncate font-medium">{name}</div>
                      {s.first_air_date ? (
                        <div className="text-xs text-zinc-600 dark:text-zinc-400">First aired: {s.first_air_date}</div>
                      ) : null}
                    </button>
                  );
                })}
              </div>
            </>
          )}
        </div>

        <div className="rounded-md border p-4">
          <h2 className="text-base font-medium">3) Services (availability) → Dates/times</h2>

          {!selectedShow ? (
            <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">Select a show.</p>
          ) : (
            <>
              <div className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
                <span className="font-medium text-zinc-900 dark:text-zinc-100">{selectedShow.name}</span>
                <span className="ml-2 font-mono text-xs">tmdb:{selectedShow.tmdbId}</span>
              </div>

              {availabilityState.status === "loading" && (
                <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">Loading…</p>
              )}
              {availabilityState.status === "error" && (
                <>
                  <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">
                    Error: {availabilityState.message}
                    {availabilityState.httpStatus ? ` (HTTP ${availabilityState.httpStatus})` : ""}
                  </p>
                  {availabilityState.body !== undefined && <PrettyJson value={availabilityState.body} />}
                </>
              )}

              {availabilityState.status === "success" && (
                <>
                  <div className="mt-3 flex items-center justify-between gap-3">
                    <div className="text-xs text-zinc-600 dark:text-zinc-400">
                      Snapshot: <span className="font-mono">{availabilityState.body.retrieved_at}</span>
                    </div>
                    <button
                      className="rounded-md border px-3 py-1.5 text-xs"
                      onClick={async () => {
                        setPlanState({ status: "loading" });
                        try {
                          const parsedHorizon = Number.parseInt(horizonDaysText.trim() || "30", 10);
                          const horizon_days = Number.isFinite(parsedHorizon) ? parsedHorizon : 30;
                          const permanent_service_ids = permanentServiceIdsText
                            .split(",")
                            .map((s) => s.trim())
                            .filter((s) => s.length > 0);

                          const requestBody = {
                            country: (country.trim() || "US").toUpperCase(),
                            horizon_days,
                            permanent_service_ids,
                            assessments: availabilityState.body.assessments,
                          };

                          const url = `${baseUrl}/plan/v1/generate`;
                          const result = await fetchJsonWithInit<PlanResponseV1>(url, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify(requestBody),
                          });
                          setPlanState({ status: "success", ...result });
                        } catch (err: unknown) {
                          const e = normalizeFetchError(err);
                          setPlanState({ status: "error", message: e.message, httpStatus: e.httpStatus, body: e.body });
                        }
                      }}
                    >
                      Generate plan
                    </button>
                  </div>

                  {planState.status === "loading" && (
                    <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">Planning…</p>
                  )}
                  {planState.status === "error" && (
                    <>
                      <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">
                        Plan error: {planState.message}
                        {planState.httpStatus ? ` (HTTP ${planState.httpStatus})` : ""}
                      </p>
                      {planState.body !== undefined && <PrettyJson value={planState.body} />}
                    </>
                  )}
                  {planState.status === "success" && (
                    <>
                      <p className="mt-3 text-xs text-zinc-600 dark:text-zinc-400">
                        Plan generated at <span className="font-mono">{planState.body.generated_at}</span>
                      </p>
                      {planState.body.questions && planState.body.questions.length > 0 && (
                        <div className="mt-2 rounded-md border p-2">
                          <div className="text-sm font-medium">Questions</div>
                          <div className="mt-1 flex flex-col gap-1">
                            {planState.body.questions.map((q) => (
                              <div key={q.id} className="text-xs text-zinc-600 dark:text-zinc-400">
                                <span className="font-mono">{q.key}</span>: {q.prompt}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {planState.body.events.length > 0 ? (
                        <div className="mt-2 flex flex-col gap-2">
                          {planState.body.events.map((e, idx) => (
                            <div key={`${e.service_id}-${e.action}-${idx}`} className="rounded-md border p-2">
                              <div className="flex items-center justify-between gap-3">
                                <div className="text-sm font-medium">
                                  {e.action} <span className="font-mono text-xs">{e.service_id}</span>
                                </div>
                                <div className="text-xs text-zinc-600 dark:text-zinc-400">
                                  <span className="font-mono">{e.effective_at}</span>
                                </div>
                              </div>
                              <div className="mt-1 text-xs text-zinc-600 dark:text-zinc-400">
                                titles: <span className="font-mono">{e.title_ids.join(", ")}</span>
                              </div>
                              <div className="mt-1 text-xs text-zinc-600 dark:text-zinc-400">
                                reasons: <span className="font-mono">{e.reason_codes.join(", ")}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">No plan events.</p>
                      )}
                    </>
                  )}

                  <div className="mt-3 flex flex-col gap-2">
                    {serviceList.map((a) => {
                      const isSelected = selectedService?.service_id === a.service_id;
                      return (
                        <button
                          key={`${a.service_id}-${a.provider_category}-${a.availability_now}`}
                          className={`rounded-md border px-3 py-2 text-left text-sm ${
                            isSelected ? "bg-zinc-50 dark:bg-zinc-900" : "bg-transparent"
                          }`}
                          onClick={async () => {
                            setSelectedService({
                              service_id: a.service_id,
                              provider_category: a.provider_category,
                              availability_now: a.availability_now,
                              confidence: a.confidence,
                            });
                            setEpisodesState({ status: "loading" });
                            try {
                              const searchUrl = `${baseUrl}/providers/tvmaze/search/shows?q=${encodeURIComponent(
                                selectedShow.name
                              )}`;
                              const search = await fetchJson<ProviderEnvelope<TvmazeSearchResult>>(searchUrl);
                              const firstId = search.body.data?.[0]?.show?.id;
                              if (!firstId) {
                                throw Object.assign(new Error("No TVmaze match found"), {
                                  httpStatus: 404,
                                  body: search.body,
                                });
                              }
                              const showUrl = `${baseUrl}/providers/tvmaze/shows/${encodeURIComponent(
                                String(firstId)
                              )}?embed=episodes`;
                              const result = await fetchJson<ProviderEnvelope<TvmazeShowWithEpisodes>>(showUrl);
                              setEpisodesState({ status: "success", ...result });
                            } catch (err: unknown) {
                              const e = normalizeFetchError(err);
                              setEpisodesState({ status: "error", message: e.message, httpStatus: e.httpStatus, body: e.body });
                            }
                          }}
                        >
                          <div className="flex items-center justify-between gap-3">
                            <div className="truncate font-mono text-xs">{a.service_id}</div>
                            <div className="text-xs text-zinc-600 dark:text-zinc-400">
                              {a.provider_category} • now:{a.availability_now} • {a.confidence}
                            </div>
                          </div>
                        </button>
                      );
                    })}

                    {serviceList.length === 0 && (
                      <p className="text-sm text-zinc-600 dark:text-zinc-400">No services returned.</p>
                    )}
                  </div>

                  {selectedService ? (
                    <div className="mt-4">
                      <h3 className="text-sm font-medium">Air dates/times</h3>
                      <p className="mt-1 text-xs text-zinc-600 dark:text-zinc-400">
                        Availability is a best-effort snapshot at {availabilityState.body.retrieved_at}.
                      </p>

                      {episodesState.status === "loading" && (
                        <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">Loading…</p>
                      )}
                      {episodesState.status === "error" && (
                        <>
                          <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
                            Error: {episodesState.message}
                            {episodesState.httpStatus ? ` (HTTP ${episodesState.httpStatus})` : ""}
                          </p>
                          {episodesState.body !== undefined && <PrettyJson value={episodesState.body} />}
                        </>
                      )}
                      {episodesState.status === "success" && (
                        <div className="mt-2 max-h-96 overflow-auto rounded-md border p-3">
                          <div className="flex flex-col gap-4">
                            <div className="text-xs text-zinc-600 dark:text-zinc-400">
                              {episodeAirTimes.nextAir ? `Next: ${episodeAirTimes.nextAir}` : "Next: (none)"}
                              {episodeAirTimes.lastAir ? ` • Last: ${episodeAirTimes.lastAir}` : ""}
                            </div>

                            <div>
                              <div className="text-xs font-medium">Upcoming (next 5)</div>
                              {episodeAirTimes.upcoming.length > 0 ? (
                                <ul className="mt-1 list-disc pl-5 text-sm">
                                  {episodeAirTimes.upcoming.map((t) => (
                                    <li key={`up-${t}`}>{t}</li>
                                  ))}
                                </ul>
                              ) : (
                                <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">None.</p>
                              )}
                            </div>

                            <div>
                              <div className="text-xs font-medium">Past (most recent 5)</div>
                              {episodeAirTimes.past.length > 0 ? (
                                <ul className="mt-1 list-disc pl-5 text-sm">
                                  {episodeAirTimes.past.map((t) => (
                                    <li key={`past-${t}`}>{t}</li>
                                  ))}
                                </ul>
                              ) : (
                                <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">None.</p>
                              )}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ) : null}
                </>
              )}
            </>
          )}
        </div>
      </section>
    </main>
  );
}
