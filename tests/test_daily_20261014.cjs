const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
require('../app/frontend/algorithms.js');const {traces,renderExtraState}=require('../app/frontend/algorithms-extra.js');
const ctx={};vm.createContext(ctx);vm.runInContext(fs.readFileSync('solutions/javascript/0021.js','utf8')+';globalThis.Node=ListNode',ctx);
const arrays=[[]];function make(a,d){if(a.length)arrays.push(a);if(d)for(const v of [-1,0,1])if(!a.length||v>=a.at(-1))make([...a,v],d-1)}make([],4);
const cases=[];let frames=0;
for(const a of arrays)for(const b of arrays){
 const expected=[...a,...b].sort((x,y)=>x-y),steps=traces.mergeListTrace({a,b});assert.deepEqual(steps.at(-1).result,expected);
 const all=[...a,...b],offset=a.length,stable=all.map((v,id)=>({v,id})).sort((x,y)=>x.v-y.v||x.id-y.id).map(x=>x.id);
 const walk=(s)=>{let p=s.head,ids=[];while(p!==null){assert.ok(!ids.includes(p));assert.ok(p>=0&&p<all.length);ids.push(p);p=s.links[p]}return ids};
 for(let i=0;i<steps.length;i++){const s=steps[i];assert.deepEqual(s.nums,all);const view=renderExtraState(21,s);assert.ok(!JSON.stringify(view).includes('undefined'));assert.equal(s.links.length,all.length);for(const p of s.links)assert.ok(p===null||Number.isInteger(p)&&p>=0&&p<all.length);walk(s);if(i){assert.notEqual(s.links,steps[i-1].links);assert.notEqual(s.selected,steps[i-1].selected)}if(s.phase==='advance-tail')assert.deepEqual(s.selected,stable.slice(0,s.selected.length));if(s.phase==='finished')assert.deepEqual(walk(s),stable);frames++}
 const nodes=all.map(v=>new ctx.Node(v));for(let i=0;i<nodes.length;i++)nodes[i].next=(i<offset?i+1<offset:i+1<nodes.length)?nodes[i+1]:null;
 let head=ctx.mergeTwoLists(nodes[0]&&offset?nodes[0]:null,b.length?nodes[offset]:null),out=[];while(head!==null){assert.ok(nodes.includes(head));assert.ok(!out.includes(head));out.push(head);head=head.next}assert.deepEqual(out.map(n=>nodes.indexOf(n)),stable);
 cases.push({a,b,expected});
}
const out='local/test-runners/daily-20261014';fs.mkdirSync(out,{recursive:true});fs.writeFileSync(out+'/cases.json',JSON.stringify(cases));
console.log(`21: ${cases.length} exhaustive sorted-list pairs; ${frames} independent graph frames; JS original node identities/stable ties/no cycles passed`);
