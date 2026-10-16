"""Create a versioned batch of existing fully authored lessons; never fetch the web."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app.backend.content_import import existing,digest,validate
p=argparse.ArgumentParser();p.add_argument('--day',required=True);p.add_argument('--batch-id',required=True);p.add_argument('ids',type=int,nargs='+');a=p.parse_args()
batch={'schemaVersion':1,'batchId':a.batch_id,'day':a.day,'items':[{'id':id,'sha256':digest(existing(ROOT,id))} for id in a.ids]}
validate(ROOT,batch);print(json.dumps(batch,ensure_ascii=True,indent=2))
