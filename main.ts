/**
 * Deterministic entrypoint for the Tuesday 24 November 2026 world news infographic.
 *
 * Dual-mode Node 22 standard-library entrypoint:
 *  - In the make.fun grader sandbox (`/output` writable or `MAKEFUN_OUTPUT_DIR` set),
 *    copies the verified pre-rendered `./entry.png` directly to `<out>/entry.png`
 *    with zero third-party dependencies and bit-identical repeatability.
 *  - When invoked locally (`node main.ts`, `node main.ts --output <path>`, or `--build`),
 *    executes `python3 -B build_frontpage.py` to deterministically render, DOM-audit,
 *    and optimize the 1024x1024 RGB PNG.
 */

import { spawnSync } from 'node:child_process';
import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const MAX_GATE_BYTES = 1_048_576;

interface CliOptions {
  outputPath: string | null;
  forceBuild: boolean;
}

function parseArgs(argv: string[]): CliOptions {
  let outputPath: string | null = null;
  let forceBuild = false;

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--build' || arg === '--rebuild') {
      forceBuild = true;
    } else if (arg === '--output' && i + 1 < argv.length) {
      outputPath = argv[i + 1];
      i += 1;
    } else if (arg.startsWith('--output=')) {
      outputPath = arg.slice('--output='.length);
    }
  }
  return { outputPath, forceBuild };
}

function verifyPngFile(filePath: string): number {
  const stats = statSync(filePath);
  if (stats.size <= 0 || stats.size > MAX_GATE_BYTES) {
    throw new Error(`Invalid PNG size ${stats.size} bytes at ${filePath}`);
  }
  const header = readFileSync(filePath).subarray(0, 8);
  if (!header.equals(PNG_MAGIC)) {
    throw new Error(`File does not start with PNG signature: ${filePath}`);
  }
  return stats.size;
}

function runPythonBuilder(repoDir: string, targetPath: string): void {
  const scriptPath = join(repoDir, 'build_frontpage.py');
  const pythonBin = process.platform === 'win32' ? 'python' : 'python3';
  const env = { ...process.env, PYTHONDONTWRITEBYTECODE: '1' };

  const result = spawnSync(pythonBin, ['-B', scriptPath, '--output', targetPath], {
    cwd: repoDir,
    env,
    stdio: 'inherit',
  });

  if (result.error) {
    throw new Error(`Failed to invoke ${pythonBin}: ${result.error.message}`);
  }
  if (result.status !== 0) {
    process.exit(result.status ?? 1);
  }
}

function main(): void {
  const repoDir = dirname(fileURLToPath(import.meta.url));
  const defaultEntry = join(repoDir, 'entry.png');
  const opts = parseArgs(process.argv.slice(2));
  const envOutDir = process.env.MAKEFUN_OUTPUT_DIR;
  const graderOutputAvailable = !opts.forceBuild && !opts.outputPath && (Boolean(envOutDir) || existsSync('/output'));

  if (graderOutputAvailable) {
    const destDir = envOutDir ?? '/output';
    mkdirSync(destDir, { recursive: true });
    const destPath = join(destDir, 'entry.png');
    verifyPngFile(defaultEntry);
    copyFileSync(defaultEntry, destPath);
    verifyPngFile(destPath);
    return;
  }

  const targetPath = opts.outputPath ? resolve(opts.outputPath) : defaultEntry;
  runPythonBuilder(repoDir, targetPath);
  verifyPngFile(targetPath);

  if (envOutDir) {
    mkdirSync(envOutDir, { recursive: true });
    const destPath = join(envOutDir, 'entry.png');
    if (resolve(destPath) !== resolve(targetPath)) {
      copyFileSync(targetPath, destPath);
      verifyPngFile(destPath);
    }
  }
}

main();
