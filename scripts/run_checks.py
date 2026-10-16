import subprocess,sys,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
commands=[[sys.executable,'tests/test_deployment.py'],[sys.executable,'tests/test_content_import.py'],[sys.executable,'tests/test_intake_http.py'],['node','tests/test_daily_20261014.cjs'],[sys.executable,'tests/build_merge_runners.py'],[sys.executable,'tests/test_daily_plan.py'],[sys.executable,'local/test-runners/daily-20261014/references.py'],['node','--experimental-strip-types','local/test-runners/daily-20261014/references.ts'],['dotnet','run','--project','local/test-runners/daily-20261014/csharp/Tests.csproj'],['node','tests/test_content.cjs'],['node','tests/test_daily_20261013.cjs'],['node','tests/test_core.cjs'],['node','tests/test_content_ui.cjs'],['node','tests/test_sync.cjs'],['node','tests/test_startup.cjs'],['node','tests/test_plan_sync.cjs'],[sys.executable,'tests/test_storage.py'],[sys.executable,'tests/test_routes.py'],[sys.executable,'tests/test_http.py'],[sys.executable,'local/test-runners/batch-five/references.py'],['node','--experimental-strip-types','local/test-runners/batch-five/references.ts'],['dotnet','run','--project','local/test-runners/batch-five/csharp/Tests.csproj']]
commands += [[sys.executable,'local/test-runners/daily-20261013/references.py'],['node','--experimental-strip-types','local/test-runners/daily-20261013/references.ts'],['dotnet','run','--project','local/test-runners/daily-20261013/csharp/Tests.csproj']]
for command in commands:
    if not shutil.which(command[0]):raise SystemExit('Missing existing runtime; not installed: '+command[0])
    subprocess.run(command,cwd=ROOT,check=True)
files=[str(p) for p in (ROOT/'local/test-runners/batch-five').glob('*.java')]
subprocess.run(['javac',*files],cwd=ROOT,check=True);subprocess.run(['java','-cp','local/test-runners/batch-five','RunReferences'],cwd=ROOT,check=True)
files=[str(p) for p in (ROOT/'local/test-runners/daily-20261013').glob('*.java')]
subprocess.run(['javac',*files],cwd=ROOT,check=True);subprocess.run(['java','-cp','local/test-runners/daily-20261013','DailyReferences'],cwd=ROOT,check=True)


files=[str(p) for p in (ROOT/'local/test-runners/daily-20261014').glob('*.java')]
subprocess.run(['javac',*files],cwd=ROOT,check=True);subprocess.run(['java','-cp','local/test-runners/daily-20261014','MergeReferences'],cwd=ROOT,check=True)
print('All actual checks passed; native TypeScript run is not full tsc type-check or phone QA.')
