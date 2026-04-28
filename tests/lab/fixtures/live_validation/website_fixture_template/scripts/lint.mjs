import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(new URL('..', import.meta.url).pathname);

for (const relativePath of ['src/components/SiteHeader.astro', 'src/pages/index.astro']) {
  const text = fs.readFileSync(path.join(root, relativePath), 'utf8');
  if (text.includes('\t')) {
    throw new Error(`${relativePath} contains tab indentation`);
  }
}
