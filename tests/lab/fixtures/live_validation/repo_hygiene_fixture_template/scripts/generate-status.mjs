import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(new URL('..', import.meta.url).pathname);
const truthPath = path.join(root, 'internal/truth/status.json');
const docPath = path.join(root, 'docs/STATUS.md');
const truth = JSON.parse(fs.readFileSync(truthPath, 'utf8'));

fs.writeFileSync(docPath, `# Fixture Status\n\nState: ${truth.state}\n`, 'utf8');
