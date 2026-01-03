import { getHealth } from "@/lib/api";

export default async function Home() {
  let apiStatus: string = "unknown";
  try {
    const health = await getHealth();
    apiStatus = health.status;
  } catch {
    apiStatus = "unreachable";
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col gap-6 p-10">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl font-semibold tracking-tight">PSMA</h1>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Program Subscription Manager Application
        </p>
      </header>

      <section className="rounded-md border p-4">
        <h2 className="text-base font-medium">Backend status</h2>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          API health: <span className="font-medium text-zinc-950 dark:text-zinc-50">{apiStatus}</span>
        </p>
        <p className="mt-2 text-xs text-zinc-600 dark:text-zinc-400">
          Configure via <span className="font-mono">NEXT_PUBLIC_API_BASE_URL</span>
        </p>
      </section>
    </main>
  );
}
