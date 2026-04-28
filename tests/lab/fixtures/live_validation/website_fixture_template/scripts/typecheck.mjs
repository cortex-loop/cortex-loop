import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(new URL('..', import.meta.url).pathname);
const resourcesPath = path.join(root, 'src/content/resources.ts');

if (fs.existsSync(resourcesPath)) {
  const text = fs.readFileSync(resourcesPath, 'utf8');
  for (const token of ['title', 'category', 'summary']) {
    if (!text.includes(token)) {
      throw new Error(`resources data is missing ${token}`);
    }
  }
}
