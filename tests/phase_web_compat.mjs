// Node/React SSR contracts using installed Vite; no browser/package installation.
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(path.join(root, 'web/package.json'));
const React = require('react');
const { renderToStaticMarkup } = require('react-dom/server');
const { createServer } = await import(require.resolve('vite'));
globalThis.localStorage = { getItem: () => null };
const server = await createServer({ root: path.join(root, 'web'), server: { middlewareMode: true, watch: null }, appType: 'custom' });
try {
  const { I18nProvider } = await server.ssrLoadModule('/src/lib/i18n.tsx');
  const { AuthProvider } = await server.ssrLoadModule('/src/lib/auth.tsx');
  const { SwingReplay } = await server.ssrLoadModule('/src/components/SwingReplay.tsx');
  const { ResultScreen } = await server.ssrLoadModule('/src/components/ResultScreen.tsx');
  const wrap = (component, props) => renderToStaticMarkup(React.createElement(I18nProvider, null,
    React.createElement(AuthProvider, null, React.createElement(component, props))));
  const replay = { source: { url: 'blob:test', startSec: 0, endSec: 20 }, phaseBoundaries: { '임팩트': [51,55] }, fps: 30, effSample: 3 };
  const old = wrap(SwingReplay, replay);
  const modern = wrap(SwingReplay, { ...replay, phaseBoundariesSec: { '임팩트': [11.3,11.7] } });
  const left = html => Number(html.match(/left:([0-9.]+)%/)[1]);
  assert.ok(Math.abs(left(old)-25.5)<1e-6, 'legacy history-index approximation');
  assert.ok(Math.abs(left(modern)-56.5)<1e-6, 'source seconds override compressed index');
  for (const name of ['il-ban','pro','pro2']) {
    const legacy = JSON.parse(execFileSync('git',['show',`HEAD:web/public/samples/${name}.json`],{cwd:root,encoding:'utf8',maxBuffer:8*1024*1024}));
    const fresh = JSON.parse(readFileSync(path.join(root,`web/public/samples/${name}.json`),'utf8'));
    for (const [label,result] of [['legacy',legacy],['fresh',fresh]]) {
      const html = wrap(ResultScreen,{result,isSample:true,onBack:()=>{},onLoginClick:()=>{}});
      assert.equal((html.match(/src="data:image\/jpeg;base64,/g)||[]).length,7,`${name} ${label} seven images`);
      assert.ok(!html.replace(/data:image\/jpeg;base64,[^"]+/g, '').includes('NaN'),`${name} ${label} no NaN display`);
    }
  }
  console.log('PASS: legacy/fresh results render seven images; source-time and fallback timeline contracts');
} finally {
  await server.close();
}
