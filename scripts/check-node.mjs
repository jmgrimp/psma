#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const MIN = { major: 20, minor: 9, patch: 0 };

function parseSemver(version) {
  const parts = String(version).trim().replace(/^v/, "").split(".");
  const major = Number(parts[0] ?? NaN);
  const minor = Number(parts[1] ?? NaN);
  const patch = Number(parts[2] ?? NaN);
  if (![major, minor, patch].every((n) => Number.isFinite(n))) return null;
  return { major, minor, patch };
}

function isLessThan(a, b) {
  if (a.major !== b.major) return a.major < b.major;
  if (a.minor !== b.minor) return a.minor < b.minor;
  return a.patch < b.patch;
}

function readRepoFile(relativePath) {
  try {
    const repoRoot = path.resolve(new URL("..", import.meta.url).pathname);
    return fs.readFileSync(path.join(repoRoot, relativePath), "utf8").trim();
  } catch {
    return null;
  }
}

if (process.env.PSMA_SKIP_NODE_CHECK === "1") {
  process.exit(0);
}

const current = parseSemver(process.versions.node);
if (!current) {
  console.error(`[psma] Unable to parse Node version: ${process.versions.node}`);
  process.exit(1);
}

if (isLessThan(current, MIN)) {
  const nvmrc = readRepoFile(".nvmrc");
  const nodeVersion = readRepoFile(".node-version");

  console.error(
    [
      "[psma] Unsupported Node.js version.",
      `  Current: ${process.versions.node}`,
      `  Required: >= ${MIN.major}.${MIN.minor}.${MIN.patch}`,
      "",
      "Fix:",
      "  - If you use nvm: run `nvm install && nvm use` in the repo root",
      nvmrc ? `    (.nvmrc = ${nvmrc})` : null,
      nodeVersion ? `    (.node-version = ${nodeVersion})` : null,
      "",
      "To bypass (not recommended): set PSMA_SKIP_NODE_CHECK=1",
    ]
      .filter(Boolean)
      .join("\n")
  );

  process.exit(1);
}
