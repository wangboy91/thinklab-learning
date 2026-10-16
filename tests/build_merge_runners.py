from pathlib import Path
import json
r=Path(__file__).resolve().parents[1];out=r/'local/test-runners/daily-20261014'
cases=json.loads((out/'cases.json').read_text());count=len(cases)
ts=(r/'solutions/typescript/0021.ts').read_text()+r'''
const fs=require('node:fs'),assert=require('node:assert/strict');
for(const c of JSON.parse(fs.readFileSync(__dirname+'/cases.json','utf8'))){
const nodes=[...c.a,...c.b].map(v=>new ListNode(v)),off=c.a.length;
for(let i=0;i<nodes.length;i++)nodes[i].next=(i<off?i+1<off:i+1<nodes.length)?nodes[i+1]:null;
let h=mergeTwoLists(off?nodes[0]:null,c.b.length?nodes[off]:null),result=[];
while(h!==null){assert.ok(nodes.includes(h));assert.ok(!result.includes(h));result.push(h);h=h.next}
assert.deepEqual(result.map(n=>n.val),c.expected);assert.equal(result.length,nodes.length);
const expectedIds=nodes.map((n,id)=>({v:n.val,id})).sort((a,b)=>a.v-b.v||a.id-b.id).map(n=>n.id);
assert.deepEqual(result.map(n=>nodes.indexOf(n)),expectedIds);
}console.log('21 TypeScript: all node identity/stable tie cases passed (native stripping, no tsc)');
'''
(out/'references.ts').write_text(ts)
py=(r/'solutions/python/0021.py').read_text()+'''
import json
from pathlib import Path
for c in json.loads((Path(__file__).parent/'cases.json').read_text()):
    nodes=[ListNode(v) for v in c['a']+c['b']];off=len(c['a'])
    for i,n in enumerate(nodes):n.next=nodes[i+1] if (i+1<off if i<off else i+1<len(nodes)) else None
    h=merge_two_lists(nodes[0] if off else None,nodes[off] if c['b'] else None);result=[]
    while h is not None:
        assert h in nodes and h not in result
        result.append(h);h=h.next
    expected=sorted(range(len(nodes)),key=lambda i:(nodes[i].val,i))
    assert [nodes.index(n) for n in result]==expected
    assert [n.val for n in result]==c['expected']
print('21 Python: all node identity/stable tie cases passed')
'''
(out/'references.py').write_text(py)
csdir=out/'csharp';csdir.mkdir(exist_ok=True)
(csdir/'Tests.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework></PropertyGroup></Project>')
(csdir/'Solution.cs').write_text((r/'solutions/csharp/0021.cs').read_text())
cs='''using System;using System.Linq;using System.Collections.Generic;
class Program {static void Check(bool b){if(!b)throw new Exception("identity/order failure");}
static void Test(int[] a,int[] b){var nodes=a.Concat(b).Select(v=>new ListNode(v)).ToArray();for(int i=0;i<nodes.Length;i++)nodes[i].next=(i<a.Length?i+1<a.Length:i+1<nodes.Length)?nodes[i+1]:null;var h=new Solution().MergeTwoLists(a.Length>0?nodes[0]:null,b.Length>0?nodes[a.Length]:null);var result=new List<ListNode>();while(h!=null){Check(nodes.Contains(h)&&!result.Contains(h));result.Add(h);h=h.next;}Check(result.SequenceEqual(nodes.OrderBy(n=>n.val)));}
static void Main(){
'''
(out/'Solution.java').write_text((r/'solutions/java/0021.java').read_text())
java='''import java.util.*;
public class MergeReferences {static void check(boolean b){if(!b)throw new RuntimeException("identity/order failure");}
static void test(int[] a,int[] b){List<ListNode> nodes=new ArrayList<>();for(int v:a)nodes.add(new ListNode(v));for(int v:b)nodes.add(new ListNode(v));for(int i=0;i<nodes.size();i++)nodes.get(i).next=(i<a.length?i+1<a.length:i+1<nodes.size())?nodes.get(i+1):null;ListNode h=new Solution().mergeTwoLists(a.length>0?nodes.get(0):null,b.length>0?nodes.get(a.length):null);List<ListNode> result=new ArrayList<>();while(h!=null){check(nodes.contains(h)&&!result.contains(h));result.add(h);h=h.next;}List<ListNode> expected=new ArrayList<>(nodes);expected.sort(Comparator.comparingInt(n->n.val));check(result.equals(expected));}
public static void main(String[] args){
'''
for c in cases:
    cs+='Test(new int[]{'+','.join(map(str,c['a']))+'},new int[]{'+','.join(map(str,c['b']))+'});\n'
    java+='test(new int[]{'+','.join(map(str,c['a']))+'},new int[]{'+','.join(map(str,c['b']))+'});\n'
cs+=f'Console.WriteLine("21 C#: {count} identity/order cases passed");}}}}'
java+=f'System.out.println("21 Java: {count} identity/order cases passed");}}}}'
(csdir/'Program.cs').write_text(cs);(out/'MergeReferences.java').write_text(java)
