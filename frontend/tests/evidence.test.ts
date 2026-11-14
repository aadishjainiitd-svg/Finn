import test from 'node:test';import assert from 'node:assert/strict';
import {filingExcerpt} from '../src/evidence.ts';
test('filing excerpt preserves honorifics, initials and approval conditions',()=>{
 const decision='In furtherance to our letter, the Board approved re-appointment of Mr. V. Srinivasa Rangan as Executive Director for one year, subject to approval of shareholders.';
 const text='Ref. SE/2026/148 Sub: Re-appointment of Mr. V. Srinivasa Rangan. '+decision+' Please note that further approval will be sought.';
 assert.equal(filingExcerpt(text),decision);assert(text.includes(filingExcerpt(text)));
});
