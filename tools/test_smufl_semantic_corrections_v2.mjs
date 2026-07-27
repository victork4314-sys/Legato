import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const sourcePath = path.resolve('tools/test_smufl_semantic_corrections.mjs');
let source = fs.readFileSync(sourcePath, 'utf8');
const old = "const unmuted = await run([event('electronic','mute',mute,0), event('electronic','unmute',unmute,0)]);";
const replacement = "const unmuted = await run([event('electronic','mute',mute,-0.1), event('electronic','unmute',unmute,0)]);";
if ((source.match(new RegExp(old.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')) || []).length !== 1) {
  throw new Error('Could not make the electronic unmute regression temporally explicit');
}
source = source.replace(old, replacement);
const output = path.resolve('/tmp/test-smufl-semantic-corrections.mjs');
fs.writeFileSync(output, source);
await import(pathToFileURL(output).href + '?v=' + Date.now());
