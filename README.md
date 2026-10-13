# ThinkLab

A small Chinese technical learning app: browse algorithm topics, follow representative problems and variants, step through real algorithm state, and share single-person progress via a LAN-hosted SQLite service. Two complete lessons include C#, Python, Java, JavaScript and TypeScript references. Other catalog entries remain material indexes, not completed lessons.

## Run

Python 3.11+ standard library only: `python server.py`. Default binds 127.0.0.1:8791. For a trusted single-person LAN, explicitly set LEARNING_HOST to the computer LAN address. No account isolation: every device that can reach the port can read and change the same profile. Do not publish this anonymous service to the internet. No code execution backend or external telemetry.

## Tests

`node tests.cjs`, `node test-sync.cjs`, `node test-startup.cjs`, `python test-storage.py`, `python test-http.py`. Algorithm tests generate optional Python/C#/Java runners. Rendering and real-device QA are separate from these logic tests.

## Data

SQLite stays on the service computer under data/. Never put the live database on a shared drive. Browser legacy records are imported only after pressing the import button; import adds missing fields and preserves existing server values, including deletions. Revisions reject concurrent stale updates with HTTP 409; operation IDs make retries idempotent. Offline queues explicitly remain unsaved until confirmed. Backup: `python backup-progress.py <destination>` uses SQLite backup.

Schema reserves algorithm, ai_application and system_design domains and distinct teaching formats. The latter two contain no lessons yet. Future database support replaces storage.py repository implementation.

## Repository and license

Project: ThinkLab. Repository: https://github.com/wangboy91/thinklab-learning . Original project code and authored teaching use the MIT License, copyright 2026 wangboy91; see CONTENT-LICENSE.md for third-party exclusions. Personal data, notes, snapshots and runtime files are never tracked.

## Maintain and add lessons

`dist/content.js` stores stable numeric IDs, domain/type/topic, representative problems, variants, learning formats and content blocks. `dist/app.js` contains complete lesson content and the player. `dist/algorithms.js` defines real-state traces; `dist/codes.js` stores five-language references. Update corresponding oracle and runner cases in `tests.cjs` when adding lessons; older tests do not prove new lessons correct. Do not automatically import entire external collections or claim incomplete entries are complete.

Portable Windows start: `powershell -File .\start-learning.ps1 -ListenAddress <LAN-IP> -Port 8791`. Local machine-specific instructions belong under ignored `local/`. Data backups use the SQLite backup helper, never a running raw DB file copy.

## Connection diagnostics

`/health` is a no-JavaScript connection page. `/api/health` keeps in-memory known-route counts/status/times only, without IP, User-Agent or bodies. A static first-paint title, ES5 startup guard and 6-second API deadline expose failures instead of waiting forever. SQLite locks return 503 after 1.5 seconds. These checks do not establish that a real mobile browser has been verified.
