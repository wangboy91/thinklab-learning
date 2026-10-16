from pathlib import Path
import json
r=Path(__file__).resolve().parents[1];out=r/'local/test-runners/daily-20261013'
cases=json.loads((out/'cases.json').read_text(encoding='utf-8'));ids=[3,167,219,206,104]
names={3:('lengthOfLongestSubstring','length_of_longest_substring','LengthOfLongestSubstring','lengthOfLongestSubstring'),167:('twoSumSorted','two_sum_sorted','TwoSum','twoSum'),219:('containsNearbyDuplicate','contains_nearby_duplicate','ContainsNearbyDuplicate','containsNearbyDuplicate'),206:('reverseList','reverse_list','ReverseList','reverseList'),104:('maxDepth','max_depth','MaxDepth','maxDepth')}
jshelper=r'''
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const cases=JSON.parse(fs.readFileSync(path.join(__dirname,'cases.json'),'utf8'));
function buildList(values){const nodes=values.map(v=>new ListNode(v));for(let i=0;i+1<nodes.length;i++)nodes[i].next=nodes[i+1];return {nodes,head:nodes[0]||null}}
function buildTree(values){if(!values.length||values[0]===null)return null;const root=new TreeNode(values[0]),queue=[root];let h=0,p=1;while(h<queue.length&&p<values.length){const node=queue[h++];for(const side of ['left','right'])if(p<values.length){const value=values[p++];if(value!==null){node[side]=new TreeNode(value);queue.push(node[side])}}}return root}
const functions={3:lengthOfLongestSubstring,167:twoSumSorted,219:containsNearbyDuplicate};
for(const c of cases){let actual;if(c.id===206){const original=buildList(c.args[0]);let cur=reverseList(original.head),i=0;const values=[];while(cur!==null){assert.ok(i<original.nodes.length);assert.equal(cur,original.nodes[original.nodes.length-1-i]);values.push(cur.val);cur=cur.next;i++}assert.equal(i,original.nodes.length);actual=values}else if(c.id===104){const tree=buildTree(c.args[0]),nodes=tree?[tree]:[],snap=[];for(let i=0;i<nodes.length;i++){const n=nodes[i];snap.push([n,n.left,n.right,n.val]);if(n.left)nodes.push(n.left);if(n.right)nodes.push(n.right)}actual=maxDepth(tree);for(const [n,left,right,value] of snap){assert.equal(n.left,left);assert.equal(n.right,right);assert.equal(n.val,value)}}else actual=functions[c.id](...c.args);assert.deepEqual(actual,c.expected)}
console.log("Daily references: "+cases.length+" cases passed; actual reversed node identity and tree nonmutation checked");
'''
for folder,ext,name in [('javascript','js','references.js'),('typescript','ts','references.ts')]:
    code='\n'.join((r/f'solutions/{folder}/{id:04}.{ext}').read_text(encoding='utf-8') for id in ids)+jshelper
    (out/name).write_text(code,encoding='utf-8')
pyhelper=r'''
import json
from pathlib import Path
cases=json.loads((Path(__file__).parent/'cases.json').read_text(encoding='utf-8'))
def build_list(values):
    nodes=[ListNode(v) for v in values]
    for i in range(len(nodes)-1): nodes[i].next=nodes[i+1]
    return nodes,nodes[0] if nodes else None
def build_tree(values):
    if not values or values[0] is None: return None
    root=TreeNode(values[0]);queue=[root];h=0;p=1
    while h<len(queue) and p<len(values):
        node=queue[h];h+=1
        for side in ['left','right']:
            if p>=len(values): break
            value=values[p];p+=1
            if value is not None:
                child=TreeNode(value);setattr(node,side,child);queue.append(child)
    return root
functions={3:length_of_longest_substring,167:two_sum_sorted,219:contains_nearby_duplicate}
for case in cases:
    if case['id']==206:
        nodes,head=build_list(case['args'][0]);cur=reverse_list(head);values=[];i=0
        while cur is not None:
            assert i<len(nodes) and cur is nodes[len(nodes)-1-i]
            values.append(cur.val);cur=cur.next;i+=1
        assert i==len(nodes);actual=values
    elif case['id']==104:
        root=build_tree(case['args'][0]);nodes=[root] if root else [];snapshot=[]
        for n in nodes:
            snapshot.append((n,n.left,n.right,n.val))
            if n.left is not None: nodes.append(n.left)
            if n.right is not None: nodes.append(n.right)
        actual=max_depth(root)
        for n,left,right,val in snapshot: assert n.left is left and n.right is right and n.val==val
    else: actual=functions[case['id']](*case['args'])
    assert actual==case['expected'],case
print('Daily Python:',len(cases),'cases passed; node identity and tree nonmutation checked')
'''
(out/'references.py').write_text('\n'.join((r/f'solutions/python/{id:04}.py').read_text(encoding='utf-8') for id in ids)+pyhelper,encoding='utf-8')
csdir=out/'csharp';csdir.mkdir(exist_ok=True)
(csdir/'Tests.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework></PropertyGroup></Project>',encoding='utf-8')
for id in ids:
    (csdir/f'D{id}.cs').write_text((r/f'solutions/csharp/{id:04}.cs').read_text(encoding='utf-8').replace('class Solution',f'class D{id}'),encoding='utf-8')
    (out/f'D{id}.java').write_text((r/f'solutions/java/{id:04}.java').read_text(encoding='utf-8').replace('class Solution',f'class D{id}'),encoding='utf-8')
cs=r'''using System;using System.Linq;using System.Collections.Generic;
class Program {static void Check(bool ok){if(!ok)throw new Exception("Daily reference failed");}
static void ListTest(int[] values,int[] expected){var nodes=values.Select(v=>new ListNode(v)).ToArray();for(int i=0;i+1<nodes.Length;i++)nodes[i].next=nodes[i+1];var current=new D206().ReverseList(nodes.Length>0?nodes[0]:null);int pos=0;var output=new List<int>();while(current!=null){Check(pos<nodes.Length);Check(object.ReferenceEquals(current,nodes[nodes.Length-1-pos]));output.Add(current.val);current=current.next;pos++;}Check(pos==nodes.Length&&output.SequenceEqual(expected));}
static TreeNode Tree(int?[] values){if(values.Length==0||!values[0].HasValue)return null;var root=new TreeNode(values[0].Value);var q=new Queue<TreeNode>();q.Enqueue(root);int p=1;while(q.Count>0&&p<values.Length){var n=q.Dequeue();if(p<values.Length){var v=values[p++];if(v.HasValue){n.left=new TreeNode(v.Value);q.Enqueue(n.left);}}if(p<values.Length){var v=values[p++];if(v.HasValue){n.right=new TreeNode(v.Value);q.Enqueue(n.right);}}}return root;}
static void TreeTest(int?[] values,int expected){var root=Tree(values);var nodes=new List<TreeNode>();if(root!=null)nodes.Add(root);for(int i=0;i<nodes.Count;i++){var n=nodes[i];if(n.left!=null)nodes.Add(n.left);if(n.right!=null)nodes.Add(n.right);}var snapshot=nodes.Select(n=>(node:n,left:n.left,right:n.right,value:n.val)).ToArray();Check(new D104().MaxDepth(root)==expected);foreach(var item in snapshot)Check(item.node.left==item.left&&item.node.right==item.right&&item.node.val==item.value);}
static void Main(){
'''
java=r'''import java.util.*;
public class DailyReferences {static void check(boolean ok){if(!ok)throw new RuntimeException("Daily reference failed");}
static void listTest(int[] values,int[] expected){ListNode[] nodes=new ListNode[values.length];for(int i=0;i<nodes.length;i++)nodes[i]=new ListNode(values[i]);for(int i=0;i+1<nodes.length;i++)nodes[i].next=nodes[i+1];ListNode cur=new D206().reverseList(nodes.length>0?nodes[0]:null);int pos=0;ArrayList<Integer> output=new ArrayList<>();while(cur!=null){check(pos<nodes.length);check(cur==nodes[nodes.length-1-pos]);output.add(cur.val);cur=cur.next;pos++;}check(pos==nodes.length&&output.size()==expected.length);for(int i=0;i<expected.length;i++)check(output.get(i)==expected[i]);}
static TreeNode tree(Integer[] values){if(values.length==0||values[0]==null)return null;TreeNode root=new TreeNode(values[0]);Queue<TreeNode> q=new ArrayDeque<>();q.add(root);int p=1;while(!q.isEmpty()&&p<values.length){TreeNode n=q.remove();if(p<values.length){Integer v=values[p++];if(v!=null){n.left=new TreeNode(v);q.add(n.left);}}if(p<values.length){Integer v=values[p++];if(v!=null){n.right=new TreeNode(v);q.add(n.right);}}}return root;}
static void treeTest(Integer[] values,int expected){TreeNode root=tree(values);List<TreeNode> nodes=new ArrayList<>();if(root!=null)nodes.add(root);for(int i=0;i<nodes.size();i++){TreeNode n=nodes.get(i);if(n.left!=null)nodes.add(n.left);if(n.right!=null)nodes.add(n.right);}IdentityHashMap<TreeNode,TreeNode[]> edges=new IdentityHashMap<>();IdentityHashMap<TreeNode,Integer> vals=new IdentityHashMap<>();for(TreeNode n:nodes){edges.put(n,new TreeNode[]{n.left,n.right});vals.put(n,n.val);}check(new D104().maxDepth(root)==expected);for(TreeNode n:nodes)check(n.left==edges.get(n)[0]&&n.right==edges.get(n)[1]&&n.val==vals.get(n));}
public static void main(String[] args){
'''
def literal(x):
    if isinstance(x,list):return 'new int[]{'+','.join(map(str,x))+'}'
    return json.dumps(x,ensure_ascii=True) if isinstance(x,(str,bool)) else str(x)
for c in cases:
    id,args,expected=c['id'],c['args'],c['expected']
    if id==206:cs+='ListTest('+literal(args[0])+','+literal(expected)+');\n';java+='listTest('+literal(args[0])+','+literal(expected)+');\n'
    elif id==104:
        values=','.join('null' if v is None else str(v) for v in args[0])
        cs+='TreeTest(new int?[]{'+values+'},'+str(expected)+');\n';java+='treeTest(new Integer[]{'+values+'},'+str(expected)+');\n'
    else:
        ccall=f'new D{id}().{names[id][2]}('+','.join(literal(v) for v in args)+')'
        jcall=f'new D{id}().{names[id][3]}('+','.join(literal(v) for v in args)+')'
        cs+='Check('+ccall+('.SequenceEqual('+literal(expected)+')' if isinstance(expected,list) else '=='+literal(expected))+');\n'
        java+='check('+('Arrays.equals('+jcall+','+literal(expected)+')' if isinstance(expected,list) else jcall+'=='+literal(expected))+');\n'
cs+='Console.WriteLine("Daily C#: '+str(len(cases))+' cases passed, node identity/tree nonmutation");}}'
java+='System.out.println("Daily Java: '+str(len(cases))+' cases passed, node identity/tree nonmutation");}}'
(csdir/'Program.cs').write_text(cs,encoding='utf-8');(out/'DailyReferences.java').write_text(java,encoding='utf-8')

