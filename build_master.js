const fs = require('fs');
const path = require('path');

function parseXMLItems(xmlPath) {
  const text = fs.readFileSync(xmlPath, 'utf8');
  const items = [];
  const itemRegex = /<item>([\s\S]*?)<\/item>/g;
  let m;
  while ((m = itemRegex.exec(text)) !== null) {
    const block = m[1];
    const get = (tag) => {
      const r = new RegExp(`<${tag}>([\\s\\S]*?)<\\/${tag}>`);
      const mm = r.exec(block);
      if (!mm) return '';
      return mm[1].trim()
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&amp;/g, '&')
        .replace(/&quot;/g, '"')
        .replace(/&apos;/g, "'");
    };
    const title = get('title');
    const link = get('link');
    const description = get('description');
    const imageUrl = get('imageUrl');
    const pubDate = get('pubDate');
    const importance = get('importance');
    if (!title || !link) continue;
    items.push({ title, link, description, imageUrl, pubDate, importance });
  }
  return items;
}

const files = [
  'bbc_world.xml',
  'fox_news_world.xml',
  'nyt_world.xml',
  'guardian_world.xml',
  'france24.xml',
  'washington_post.xml',
  'abc_news_international.xml',
  'politico.xml',
  'cbc_world.xml',
  'npr_world.xml',
  'international-war.xml'
];

let all = [];
for (const f of files) {
  const p = path.join(__dirname, f);
  if (!fs.existsSync(p)) { console.log('missing', p); continue; }
  all = all.concat(parseXMLItems(p));
}

// Filter: must have image
all = all.filter(it => it.imageUrl && it.imageUrl.trim() !== '');

// Deduplicate by link
const seen = new Set();
all = all.filter(it => {
  if (seen.has(it.link)) return false;
  seen.add(it.link);
  return true;
});

// Parse dates for sorting
function toEpoch(d) {
  if (!d) return 0;
  try { return new Date(d).getTime(); } catch (e) { return 0; }
}

all.sort((a, b) => toEpoch(b.pubDate) - toEpoch(a.pubDate));

const top10 = all.slice(0, 10);

const now = new Date().toUTCString();
let out = `<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0">\n  <channel>\n    <title>International Master - Top Stories</title>\n    <lastBuildDate>${now}</lastBuildDate>\n    <description>SPZ News Aggregator</description>\n`;

for (const it of top10) {
  function decodeEntities(str) {
    return str.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&').replace(/&quot;/g, '"');
  }
  const descRaw = decodeEntities(it.description);
  const descEsc = descRaw
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
  out += `    <item>\n`;
  out += `      <title>${it.title.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</title>\n`;
  out += `      <link>${it.link}</link>\n`;
  out += `      <description>${descEsc}</description>\n`;
  out += `      <imageUrl>${it.imageUrl}</imageUrl>\n`;
  out += `      <pubDate>${it.pubDate}</pubDate>\n`;
  if (it.importance) out += `      <importance>${it.importance}</importance>\n`;
  out += `    </item>\n`;
}

out += `  </channel>\n</rss>\n`;

fs.writeFileSync(path.join(__dirname, 'international-master.xml'), out, 'utf8');
console.log('Wrote', top10.length, 'items to international-master.xml');
for (const it of top10) {
  console.log('-', it.title.substring(0, 80));
}
