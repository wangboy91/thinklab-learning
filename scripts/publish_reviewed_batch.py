"""Local maintainer action only. Does not run incoming solution/trace code or tests."""
import argparse,json,os,shutil,subprocess,sys,tempfile,datetime,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app.backend.content_import import validate,digest,safe_path,LANGUAGES,canonical
def publish(root,batch,review,expected):
    root=Path(root);result=validate(root,batch)
    if expected!=digest(batch) or review.get('batchSha256')!=expected or review.get('schemaVersion')!=1:raise ValueError('Review digest/version mismatch')
    # Review is a trusted local file, never accepted through the HTTP endpoint.
    tests=review.get('checks',{})
    if review.get('approved') is not True or not isinstance(review.get('reviewer'),str) or not review['reviewer'].strip() or any(tests.get(k)!='passed' for k in ['rights','semantics','traceOracle','fiveLanguages','ui']):raise ValueError('Explicit local review and passing validation evidence required')
    evidence=review.get('evidence')
    if not isinstance(evidence,str) or not evidence.strip():raise ValueError('Review must identify the actual test report/evidence')
    if not result['pendingReview']:return dict(result,status='already_published')
    local=safe_path(root,'local');local.mkdir(exist_ok=True);lock=local/'content-publish.lock'
    try:lock.mkdir()
    except FileExistsError:raise RuntimeError('Another publication or stale publication lock exists; inspect it before retrying')
    backup=Path(tempfile.mkdtemp(prefix='before-content-import-',dir=local));written={};old_catalog=None;old_dist={}
    try:
        catalogpath=safe_path(root,'content/catalog.json');old_catalog=catalogpath.read_bytes();catalog=json.loads(old_catalog)
        (backup/'catalog.json').write_bytes(old_catalog);(backup/'review.json').write_bytes(canonical(review));(backup/'batch.json').write_bytes(canonical(batch))
        for item in batch['items']:
            if item['id'] not in result['pendingReview']:continue
            id=item['id'];candidate=item['candidate'];lesson=candidate['lesson']
            paths={f'content/problems/{id:04}.json':json.dumps(lesson,ensure_ascii=False,indent=2)+'\n'}
            paths.update({f'solutions/{lang}/{id:04}.{ext}':candidate['solutions'][lang].strip()+'\n' for lang,ext in LANGUAGES.items()})
            for relative,value in paths.items():
                path=safe_path(root,relative);path.parent.mkdir(parents=True,exist_ok=True)
                with path.open('x',encoding='utf-8',newline='\n') as f:f.write(value)
                written[path]=path.read_bytes()
            entry=next((e for e in catalog['catalog'] if e['id']==id),None)
            # Preserve existing pending catalog metadata except fields made authoritative by the reviewed lesson.
            metadata={'id':id,'title':lesson['title'],'topic':lesson['topic'],'difficulty':lesson['difficulty'],'officialUrl':lesson['source']['officialUrl'],'domain':'algorithm','type':'algorithm','learningFormat':'state_steps'}
            if entry is None:catalog['catalog'].append(dict(metadata,sources=[{'kind':'official_link','url':metadata['officialUrl']}]))
            else:entry.update(metadata)
        if catalogpath.read_bytes()!=old_catalog:raise RuntimeError('Catalog changed concurrently; publication stopped')
        newcatalog=(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n').encode('utf-8');tmp=backup/'catalog.next';tmp.write_bytes(newcatalog);os.replace(tmp,catalogpath);written[catalogpath]=newcatalog
        # Build only trusted project code; solution files are read as text. No imported code is run.
        staged=backup/'dist';subprocess.run([sys.executable,str(root/'scripts/build_content.py'),'--out',str(staged.relative_to(root))],cwd=root,check=True)
        for source in staged.iterdir():
            target=safe_path(root,'dist/'+source.name);old_dist[target]=target.read_bytes() if target.exists() else None
            if target.exists():(backup/('dist-'+source.name)).write_bytes(old_dist[target])
            target.parent.mkdir(exist_ok=True);os.replace(source,target);written[target]=target.read_bytes()
        return dict(validate(root,batch),status='published',backup=str(backup),nextStep='Submit the unchanged batch to intake --apply to merge the daily plan')
    except BaseException:
        # Revert only bytes written by this operation; preserve later external edits.
        for path,data in reversed(list(written.items())):
            if path.exists() and path.read_bytes()==data:
                if path in old_dist:
                    if old_dist[path] is None:path.unlink()
                    else:path.write_bytes(old_dist[path])
                elif path==root/'content/catalog.json' and old_catalog is not None:path.write_bytes(old_catalog)
                else:path.unlink()
        raise
    finally:lock.rmdir()
def main():
    p=argparse.ArgumentParser();p.add_argument('batch',type=Path);p.add_argument('--review-file',type=Path,required=True);p.add_argument('--expected-sha256',required=True);a=p.parse_args()
    print(json.dumps(publish(ROOT,json.loads(a.batch.read_text(encoding='utf-8')),json.loads(a.review_file.read_text(encoding='utf-8')),a.expected_sha256),ensure_ascii=True))
if __name__=='__main__':main()
