import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(new URL('..', import.meta.url).pathname);

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

const resourcesPage = read('src/pages/resources.astro');
if (/client:(load|only)/.test(resourcesPage)) {
  throw new Error('resources filter uses an over-eager hydration directive');
}
if (!/client:(idle|visible)/.test(resourcesPage)) {
  throw new Error('resources filter must use client:idle or client:visible');
}
if (/<script\b/.test(resourcesPage)) {
  throw new Error('resources page uses an inline script instead of an island');
}
if (/<header\b|<footer\b|<SiteHeader\b/.test(resourcesPage)) {
  throw new Error('resources page introduced local chrome');
}

const islandDir = path.join(root, 'src/components/islands');
const islandFiles = fs.existsSync(islandDir)
  ? fs.readdirSync(islandDir).filter((name) => name.startsWith('ResourceFilter.'))
  : [];
if (islandFiles.length === 0) {
  throw new Error('ResourceFilter island is missing from src/components/islands');
}
const islandText = islandFiles.map((name) => read(`src/components/islands/${name}`)).join('\n');
if (!islandText.includes('data-resource-filter')) {
  throw new Error('ResourceFilter island is missing data-resource-filter marker');
}

const dataText = read('src/content/resources.ts');
for (const token of ['title', 'category', 'summary']) {
  if (!dataText.includes(token)) {
    throw new Error(`resources data is missing ${token}`);
  }
}

const headerText = read('src/components/SiteHeader.astro');
if (!headerText.includes('href="/resources/"') || !headerText.includes('>Resources<')) {
  throw new Error('site header is missing the Resources navigation link');
}
