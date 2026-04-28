import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(new URL('..', import.meta.url).pathname);

for (const relativePath of [
  'src/layouts/Layout.astro',
  'src/components/SiteHeader.astro',
  'src/components/ApprovedResourceShell.astro',
  'src/pages/index.astro',
]) {
  if (!fs.existsSync(path.join(root, relativePath))) {
    throw new Error(`missing required source file: ${relativePath}`);
  }
}
