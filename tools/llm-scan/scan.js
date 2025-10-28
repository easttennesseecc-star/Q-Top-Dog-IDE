#!/usr/bin/env node
// Local LLM & assistant scanner (non-invasive)
// - checks PATH for known LLM CLIs
// - lists running processes (Windows)
// - checks common install paths for known binaries
// Outputs report to tools/llm-scan/report.json

const fs = require('fs');
const path = require('path');
const { execSync, spawnSync } = require('child_process');

const candidates = [
  { name: 'gpt4all', bin: 'gpt4all' },
  { name: 'llama.cpp', bin: 'llama.cpp' },
  { name: 'gpt-4o', bin: 'gpt4o' },
  { name: 'gemini-local', bin: 'gemini' },
  { name: 'local-chatgpt', bin: 'chatgpt' },
  { name: 'microsoft-azure-openai-local', bin: 'azureopenai' },
];

function whichSync(cmd) {
  try {
    const out = spawnSync(process.platform === 'win32' ? 'where' : 'which', [cmd], { encoding: 'utf8' });
    if (out.status === 0) return out.stdout.split(/\r?\n/)[0];
  } catch (e) {}
  return null;
}

function checkPaths() {
  const found = [];
  candidates.forEach(c => {
    const p = whichSync(c.bin);
    if (p) found.push({ name: c.name, bin: c.bin, path: p, source: 'PATH' });
  });
  return found;
}

function listProcesses() {
  try {
    if (process.platform === 'win32') {
      const out = execSync('tasklist /FO CSV /NH', { encoding: 'utf8' });
      const lines = out.trim().split(/\r?\n/);
      return lines.map(l => {
        const parts = l.split(',').map(s => s.replace(/^"|"$/g, ''));
        return { image: parts[0], pid: parts[1] };
      });
    } else {
      const out = execSync('ps -eo pid,comm', { encoding: 'utf8' });
      const lines = out.trim().split(/\r?\n/).slice(1);
      return lines.map(l => {
        const m = l.trim().match(/^(\d+)\s+(.+)$/);
        return m ? { pid: m[1], image: m[2] } : null;
      }).filter(Boolean);
    }
  } catch (e) {
    return [];
  }
}

function checkCommonInstalls() {
  const places = [];
  if (process.platform === 'win32') {
    const prog = process.env['ProgramFiles'] || 'C:\\Program Files';
    const pf86 = process.env['ProgramFiles(x86)'] || 'C:\\Program Files (x86)';
    places.push(path.join(prog, 'gpt4all'));
    places.push(path.join(pf86, 'gpt4all'));
    places.push(path.join(process.env.HOMEPATH || '', '.local', 'bin'));
  } else {
    places.push('/usr/local/bin');
    places.push('/opt');
    places.push(path.join(process.env.HOME || '', '.local', 'bin'));
  }
  const found = [];
  places.forEach(p => {
    try {
      if (fs.existsSync(p)) {
        found.push({ path: p, files: fs.readdirSync(p).slice(0,50) });
      }
    } catch (e) {}
  });
  return found;
}

function main() {
  const report = { timestamp: new Date().toISOString(), platform: process.platform, pathFound: checkPaths(), processes: listProcesses().slice(0,200), installs: checkCommonInstalls() };
  const outdir = path.join(__dirname);
  const outfile = path.join(outdir, 'report.json');
  fs.writeFileSync(outfile, JSON.stringify(report, null, 2));
  console.log('Scan complete. Report written to', outfile);
}

main();
