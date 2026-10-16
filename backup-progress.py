# Transitional backup command.
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).parent/'scripts/backup_progress.py'),run_name='__main__')
