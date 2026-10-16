"""Build authored, validated sources only. Never read local/imports or personal data."""
from pathlib import Path
import argparse,json,shutil,hashlib
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--out',default='dist');args=p.parse_args()
out=(ROOT/args.out).resolve()
if not out.is_relative_to(ROOT):raise SystemExit('Output must stay inside project')
out.mkdir(parents=True,exist_ok=True)
required=['title','concept','question','think','hints','explain','why','complexity','errors','exampleText','challenge','boardLabel','examples','source']
lessons={};codes={}
languages={'C#':('csharp','cs'),'Python':('python','py'),'Java':('java','java'),'JavaScript（Node.js）':('javascript','js'),'TypeScript':('typescript','ts')}
for file in sorted((ROOT/'content/problems').glob('*.json')):
    id=int(file.stem);lesson=json.loads(file.read_text(encoding='utf-8'))
    if id in lessons or lesson.get('id')!=id:raise SystemExit('Duplicate/mismatched lesson id')
    if any(not lesson.get(field) for field in required):raise SystemExit(f'Incomplete lesson {id}')
    if len(lesson['hints'])<3 or not lesson['examples']:raise SystemExit(f'Missing teaching steps {id}')
    if not lesson['source']['officialUrl'].startswith('https://leetcode.com/problems/'):raise SystemExit('Official provenance missing')
    variants={}
    for lang,(folder,ext) in languages.items():
        path=ROOT/f'solutions/{folder}/{id:04}.{ext}'
        if not path.is_file():raise SystemExit(f'Missing {lang} reference {id}')
        variants[lang]=path.read_text(encoding='utf-8').strip()
    lessons[id]=lesson;codes[id]=variants
catalog=json.loads((ROOT/'content/catalog.json').read_text(encoding='utf-8'));ids=[entry['id'] for entry in catalog['catalog']]
if len(ids)!=len(set(ids)):raise SystemExit('Duplicate catalog id')
for entry in catalog['catalog']:entry['complete']=entry['id'] in lessons;entry['status']='complete' if entry['complete'] else 'pending'
routes=json.loads((ROOT/'content/routes/routes.json').read_text(encoding='utf-8'))
for route in routes:
    if len(route['problemIds'])!=len(set(route['problemIds'])) or not set(route['problemIds'])<=set(ids):raise SystemExit('Invalid route IDs')
for path in (ROOT/'app/frontend').iterdir():
    if path.suffix in ['.js','.css','.html']:shutil.copyfile(path,out/path.name)
for filename,name,data in [('content.js','CONTENT',catalog),('codes.js','CODES',codes),('lessons.js','LESSONS',lessons),('routes.js','ROUTES',routes)]:
    (out/filename).write_text('window.'+name+'='+json.dumps(data,ensure_ascii=False)+';',encoding='utf-8')
print(f'Built {len(lessons)} complete lessons / {len(ids)} catalog entries / {len(codes)*5} reference files into {out.name}')
