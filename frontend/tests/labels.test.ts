import test from 'node:test';import assert from 'node:assert/strict';
import {thesisLabel,eventType,weekday} from '../src/product.ts';
// Regression: the card compared against 'weakening' (a holding-level status), so
// per-filing adverse thesis evidence (backend 'weakens') was never shown in red.
test('per-filing thesis effects map to reference labels and never imply health',()=>{
 assert.deepEqual(thesisLabel('weakens'),['Weakens your thesis','red']);
 assert.deepEqual(thesisLabel('supports'),['Supports your thesis','green']);
 assert.deepEqual(thesisLabel('neutral'),['No thesis effect found','']);
 for(const missing of ['unknown',null,undefined,'weakening'])assert.deepEqual(thesisLabel(missing),['Thesis not assessed','']);
});
test('event type uses verified category, then description, never invents one',()=>{
 assert.equal(eventType({kind:'price'}),'Unusual move');
 assert.equal(eventType({kind:'filing',category:'Board change'}),'Board change');
 assert.equal(eventType({kind:'filing',description:'Outcome of Board Meeting · Results'}),'Outcome of Board Meeting');
 assert.equal(eventType({kind:'filing'}),'Disclosure');
 assert.equal(eventType({kind:'filing',category:'management'}),'Management');
});
test('header date is IST weekday style',()=>{
 assert.equal(weekday(new Date('2026-11-14T19:00:00Z')),'Sun 15 Nov');
});
