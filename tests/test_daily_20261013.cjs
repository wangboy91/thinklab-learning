const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),cp=require('node:child_process');
const root=path.resolve(__dirname,'..');require('../app/frontend/algorithms.js');const {traces,renderExtraState}=require('../app/frontend/algorithms-extra.js');
const longest=s=>{let best=0;for(let i=0;i<s.length;i++){const seen=new Set();for(let j=i;j<s.length;j++){if(seen.has(s[j]))break;seen.add(s[j]);best=Math.max(best,j-i+1)}}return best};
const nearby=(a,k)=>{for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++)if(a[i]===a[j]&&j-i<=k)return true;return false};
function treeFrom(a){if(!a.length||a[0]===null)return null;const root={val:a[0],left:null,right:null},q=[root];let h=0,p=1;while(h<q.length&&p<a.length){const n=q[h++];for(const side of ['left','right'])if(p<a.length){const value=a[p++];if(value!==null){n[side]={val:value,left:null,right:null};q.push(n[side])}}}return root}
function treeOracle(a){const root=treeFrom(a);if(!root)return 0;const stack=[[root,1]];let best=0;while(stack.length){const [n,d]=stack.pop();best=Math.max(best,d);if(n.left)stack.push([n.left,d+1]);if(n.right)stack.push([n.right,d+1])}return best}
const cases=[];const add=(id,args,expected)=>cases.push({id,args,expected});
for(const s of ['',' ','abcabcbb','bbbbb','pwwkew','abba','dvdf','tmmzuxt','aA','a!a','a b a'])add(3,[s],longest(s));
for(const [a,t,e] of [[[2,7,11,15],9,[1,2]],[[2,3,4],6,[1,3]],[[-1,0],-1,[1,2]],[[2,2],4,[1,2]],[[-5,-2,1,8],3,[1,4]],[[0,1,3,4],5,[2,4]],[[1,2,3,4],7,[3,4]],[[0,0,1],0,[1,2]],[[],0,[]]])add(167,[a,t],e);
for(const [a,k] of [[[1,2,3,1],3],[[1,0,1,1],1],[[1,2,3,1,2,3],2],[[1,2,1],1],[[1,2,1],2],[[1,1],0],[[-1,0,-1],2],[[0,0],1],[[],3],[[1],5]])add(219,[a,k],nearby(a,k));
for(const a of [[],[0],[1,2],[1,2,3,4,5],[7,7,7],[-1,0,1,1]])add(206,[a],a.slice().reverse());
for(const a of [[],[1],[3,9,20,null,null,15,7],[1,null,2],[1,null,2,3],[0,0,0],[1,2,3,4,5,6,7],[1,null,2,null,3,null,4]])add(104,[a],treeOracle(a));
let traceCount=0;
function walk(links,start){const out=[];while(start!==null){assert.ok(!out.includes(start));assert.ok(start>=0&&start<links.length);out.push(start);start=links[start]}return out}
function check(id,e,expected){const name={3:'longestWindowTrace',167:'sortedPairTrace',219:'nearbyWindowTrace',206:'reverseListTrace',104:'treeDepthTrace'}[id],steps=traces[name](e);assert.deepEqual(steps.at(-1).result,expected);
for(let i=0;i<steps.length;i++){const s=steps[i],view=renderExtraState(id,s);assert.ok(s.text);assert.ok(!view.tokens.includes('undefined')&&!view.visual.includes('undefined'));for(const key of ['nums','chars','set','links','nodes','queue','processed'])if(Array.isArray(s[key])&&i)assert.notEqual(s[key],steps[i-1][key]);
if(id===3){if(i)assert.ok(s.best>=steps[i-1].best);const end=s.phase==='finished'?s.chars.length:s.included?s.right+1:Math.max(0,s.right),start=s.phase==='remove'?s.left+1:s.left;assert.deepEqual(new Set(s.set),new Set(s.chars.slice(start,end)));assert.equal(s.set.length,new Set(s.set).size)}
if(id===167&&s.sum!==null){assert.ok(s.left<s.right);assert.equal(s.sum,e.nums[s.left]+e.nums[s.right]);if(s.result?.length)assert.deepEqual(s.result,[s.left+1,s.right+1])}
if(id===219){assert.equal(s.set.length,new Set(s.set).size);assert.ok(s.set.length<=Math.min(e.nums.length,Math.max(0,e.k)+1));assert.deepEqual(new Set(s.set),new Set(e.nums.slice(s.left,s.end)));if(s.pair){assert.notEqual(s.pair[0],s.pair[1]);assert.equal(e.nums[s.pair[0]],e.nums[s.pair[1]]);assert.ok(s.pair[1]-s.pair[0]<=e.k)}}
if(id===206){assert.deepEqual(s.nums,e.values);for(let j=0;j<s.links.length;j++){assert.ok(s.links[j]===null||(Number.isInteger(s.links[j])&&s.links[j]>=0&&s.links[j]<s.links.length));assert.notEqual(s.links[j],j)}if(s.phase==='move-current'||s.phase==='finished'){const a=walk(s.links,s.prev),b=walk(s.links,s.current);assert.equal(a.length+b.length,e.values.length);assert.equal(new Set([...a,...b]).size,e.values.length);assert.deepEqual(a,Array.from({length:a.length},(_,j)=>a.length-1-j))}if(s.result!==null)assert.deepEqual(walk(s.links,s.prev),e.values.map((_,j)=>e.values.length-1-j))}
if(id===104){assert.equal(s.queue.length,new Set(s.queue).size);assert.equal(s.processed.length,new Set(s.processed).size);assert.ok(s.queue.every(id=>id>=0&&id<s.nodes.length));if(s.phase==='level')assert.ok(s.queue.every(id=>s.nodes[id].level===s.depth));if(s.result!==null){assert.equal(s.processed.length,s.nodes.length);assert.equal(s.queue.length,0)}}
}traceCount++}
function strings(s,d){check(3,{s},longest(s));if(d)for(const c of ['a','A','b','0',' ','!'])strings(s+c,d-1)}strings('',4);
function arrays(a,d){for(let k=0;k<=4;k++)check(219,{nums:a,k},nearby(a,k));check(206,{values:a},a.slice().reverse());if(a.length>=2){const nums=a.slice().sort((a,b)=>a-b);for(let t=-3;t<=3;t++){const pairs=[];for(let i=0;i<nums.length;i++)for(let j=i+1;j<nums.length;j++)if(nums[i]+nums[j]===t)pairs.push([i+1,j+1]);if(pairs.length===1)check(167,{nums,target:t},pairs[0])}}if(d)for(const v of [-1,0,1])arrays([...a,v],d-1)}arrays([],4);
for(const c of cases.filter(c=>c.id===104))check(104,{tree:c.args[0]},c.expected);
for(let mask=0;mask<128;mask++){const a=[0];for(let i=0;i<6;i++)a.push(mask&(1<<i)?i%3:null);check(104,{tree:a},treeOracle(a))}
assert.equal(traces.treeDepthTrace({tree:[1,null,2,3]}).at(-1).result,3);
const out=path.join(root,'local/test-runners/daily-20261013');fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,'cases.json'),JSON.stringify(cases));
const result=cp.spawnSync('python',['tests/build_daily_runners.py'],{cwd:root,encoding:'utf8'});if(result.status!==0)throw Error(result.stderr||result.stdout);
const ref=cp.spawnSync('node',[path.join(out,'references.js')],{cwd:root,encoding:'utf8'});if(ref.status!==0)throw Error(ref.stderr||ref.stdout);
console.log(ref.stdout.trim());console.log('PASS daily: '+traceCount+' independent oracle/window/edge/level checks; '+cases.length+' cases; separate runners generated.');

