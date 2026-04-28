import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(new URL('..', import.meta.url).pathname);
const truthPath = path.join(root, 'internal/truth/status.json');
const docPath = path.join(root, 'docs/STATUS.md');
const truth = JSON.parse(fs.readFileSync(truthPath, 'utf8'));
const expected = `# Fixture Status\n\nState: ${truth.state}\n`;

if (!fs.existsSync(docPath)) {
  throw new Error('docs/STATUS.md is missing');
}
const actual = fs.readFileSync(docPath, 'utf8');
if (actual !== expected) {
  throw new Error('docs/STATUS.md is stale');
}
if (truth.state !== 'ready') {
  throw new Error('status truth state is not ready');
}
