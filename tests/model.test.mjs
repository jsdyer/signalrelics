import test from 'node:test';import assert from 'node:assert/strict';import {filterRecords,csv,loadSaved,safeExternal} from '../web/model.mjs';
const a={id:'co1',title:'Modem one',groups:['modems'],terms:['network'],description:'Dial-up',makers:['Hayes'],places:[],materials:[],date:'1960–1970',start:1960,end:1970,source:'https://example.org'};const b={...a,id:'co2',title:'Undated telephone',groups:['telephones'],start:null,end:null};
test('range overlap, maker and category filters work together',()=>{assert.deepEqual(filterRecords([a,b],{from:1965,to:1980,maker:'Hayes',group:'modems'}),[a]);assert.equal(filterRecords([a,b],{from:1980}).length,0)});
test('new categories are not limited to starter groups',()=>assert.equal(filterRecords([{...a,groups:['new']}],{group:'new'}).length,1));
test('saved data is validated against known IDs',()=>assert.deepEqual([...loadSaved('["co1","bad"]',new Set(['co1']))],['co1']));
test('untrusted links and CSV formula inputs are safe',()=>{assert.equal(safeExternal('javascript:alert(1)'),'');assert.equal(safeExternal('https://user:password@example.org'),'');assert.match(csv([{...a,title:'=SUM(1)'}]),/"'=SUM\(1\)"/)});
test('undated objects sort last without fabricated dates',()=>assert.deepEqual(filterRecords([b,a]).map(r=>r.id),['co1','co2']));
