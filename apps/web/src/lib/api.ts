export function apiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
}

export async function getHealth(): Promise<{ status: string }> {
  const res = await fetch(`${apiBaseUrl()}/health`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return (await res.json()) as { status: string };
}
