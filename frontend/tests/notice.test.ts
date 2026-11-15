import {test} from 'node:test';
import assert from 'node:assert/strict';
import {noticeLine,cardHeadline} from '../src/product.ts';

test('notice line keeps the exchange words and drops the preamble',()=>{
 assert.equal(noticeLine({kind:'filing',title:'General Updates',description:'General Updates · HDFC Bank Limited has informed the Exchange about Approval from the Reserve Bank of India'}),'Approval from the Reserve Bank of India');
});
test('notice line is empty for prices, missing text, or a repeat of the title',()=>{
 assert.equal(noticeLine({kind:'price',description:'x · y'}),'');
 assert.equal(noticeLine({kind:'filing',title:'Appointment',description:'Appointment'}),'');
 assert.equal(noticeLine({kind:'filing',title:'Allotment of Securities',description:'Allotment · X Ltd has informed the Exchange about allotment of securities'}),'');
});

test('notice line trims the submitted-to-the-Exchange preamble',()=>{
 assert.equal(noticeLine({kind:'filing',title:'Financial Results',description:'Outcome · Tata Power Company Limited has submitted to the Exchange, the financial results for the period ended September 30, 2026.'}),'Financial results for the period ended September 30, 2026.');
});

test('generic subjects are replaced by the exchange words',()=>{
 assert.deepEqual(cardHeadline({kind:'filing',title:'General Updates',description:'General Updates · X Ltd has informed the Exchange about Approval from the RBI'}),{title:'Approval from the RBI',line:''});
 assert.equal(cardHeadline({kind:'filing',title:'Director appointed for one year',description:'x · X Ltd has informed the Exchange about board change'}).title,'Director appointed for one year');
});
