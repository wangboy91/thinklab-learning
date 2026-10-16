"""Isolated fixture roots only: tests never publish into the real library or personal DB."""
from pathlib import Path
import shutil,sys,copy,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
def fixture(root):
    root=Path(root)
    for name in ['app','content','solutions']:
        shutil.copytree(ROOT/name,root/name,ignore=shutil.ignore_patterns('__pycache__'))
    (root/'scripts').mkdir(exist_ok=True)
    for name in ['build_content.py','start_local.py']:shutil.copyfile(ROOT/'scripts'/name,root/'scripts'/name)
    for name in ['server.py','storage.py']:shutil.copyfile(ROOT/name,root/name)
    return root
def candidate(root,id=99001):
    from app.backend.content_import import existing
    package=copy.deepcopy(existing(root,21));package['lesson']['id']=id;package['rights']='original'
    # Synthetic reference must stay text during intake and publication.
    package['solutions']['python']="raise RuntimeError('Never execute uploaded code inside intake')"
    return {'schemaVersion':1,'batchId':'synthetic-candidate','day':'2030-1-2','items':[{'id':id,'candidate':package}]}
def reference(root,ids=(1,167),batch_id='synthetic-reference'):
    from app.backend.content_import import existing,digest
    return {'schemaVersion':1,'batchId':batch_id,'day':'2030-1-2','items':[{'id':id,'sha256':digest(existing(root,id))} for id in ids]}
