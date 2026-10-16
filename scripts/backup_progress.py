import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
from storage import SQLiteProgressStore
p=argparse.ArgumentParser();p.add_argument('destination');p.add_argument('--database',default='data/learning.sqlite3');a=p.parse_args();SQLiteProgressStore(a.database).backup(a.destination);print('SQLite backup complete')
