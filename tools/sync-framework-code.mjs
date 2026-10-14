/* Keep static lesson snippets identical to their project source. --check never writes. */
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const check = process.argv.includes('--check');
const escape = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
for (const name of readdirSync(path.join(root, 'framework')).filter(f => /^f\d{2}\.html$/.test(f))) {
  const file = path.join(root, 'framework', name);
  const before = readFileSync(file, 'utf8');
  const after = before.replace(/(<pre\b[^>]*data-source="([^"]+)"[^>]*><code[^>]*>)([\s\S]*?)(<\/code><\/pre>)/g,
    (whole, open, source, old, close) => {
      const lines = readFileSync(path.join(root, source), 'utf8').trimEnd().split('\n');
      const range = open.match(/data-lines="(\d+)-(\d+)"/);
      const excerpt = range ? lines.slice(Number(range[1]) - 1, Number(range[2])) : lines;
      if (range && Number(range[2]) > lines.length) throw new Error(`${name}: invalid range for ${source}`);
      return open + escape(excerpt.join('\n')) + close;
    });
  if (before !== after) {
    if (check) throw new Error(`${name}: snippets differ; run node tools/sync-framework-code.mjs`);
    writeFileSync(file, after);
  }
}
console.log('框架篇代码片段与工程文件一致');
