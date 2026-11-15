import {test} from 'node:test';
import assert from 'node:assert/strict';
import {personName} from '../src/product.ts';

test('person name is read from common notice phrasings',()=>{
 assert.equal(personName('Appointment of Mr Sanjay Kumar Banga as additional Executive Director'),'Sanjay Kumar Banga');
 assert.equal(personName('re-appointment of Mr. V. Srinivasa Rangan as the Whole-time Director'),'V. Srinivasa Rangan');
 assert.equal(personName('Change in Director(s) of the company.'),'');
});
