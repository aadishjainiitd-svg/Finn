import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const root=new URL('../dist/',import.meta.url);
const id=createHash('sha256').update(readFileSync(new URL('index.html',root))).digest('hex').slice(0,16);
const worker=new URL('sw.js',root);
writeFileSync(worker,readFileSync(worker,'utf8').replace('__BUILD_ID__',id));
