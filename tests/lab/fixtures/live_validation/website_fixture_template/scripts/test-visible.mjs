import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(new URL('..', import.meta.url).pathname);
const resourcesPage = path.join(root, 'src/pages/resources.astro');

if (!fs.existsSync(resourcesPage)) {
  throw new Error('resources page is missing');
}

const text = fs.readFileSync(resourcesPage, 'utf8');
if (!text.includes('ApprovedResourceShell')) {
  throw new Error('resources page does not reuse the approved resource shell');
}
if (!text.includes('ResourceFilter')) {
  throw new Error('resources page is missing the resource filter island');
}
