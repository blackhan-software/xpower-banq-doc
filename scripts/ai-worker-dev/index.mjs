#!/usr/bin/env node

// Wrap `wrangler dev` to forward provider API keys ($ANTHROPIC_API_KEY,
// $DEEPSEEK_API_KEY) from the shell, which wrangler itself does not read.
// Only keys that are actually set get forwarded; the worker reads the one
// that matches wrangler.toml's API_PROVIDER, so unset values are fine.
import { spawn } from 'node:child_process';

const args = ['dev', ...process.argv.slice(2)];
for (const key of ['ANTHROPIC_API_KEY', 'DEEPSEEK_API_KEY']) {
  if (process.env[key]) {
    args.push('--var', `${key}:${process.env[key]}`);
  }
}

const child = spawn('wrangler', args, {
  stdio: 'inherit', shell: false
});
child.on('exit', (code, signal) => {
  if (signal) process.kill(process.pid, signal);
  else process.exit(code ?? 0);
});
