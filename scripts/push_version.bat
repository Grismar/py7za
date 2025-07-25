@echo off
REM change working directory to project root
cd %~dp0\..
set PYTHONPATH=%~dp0\..
python scripts/check_version.py %1
if errorlevel 1 goto version_issue
git diff-index --quiet HEAD
if errorlevel 1 goto uncommitted_changes
call scripts/run_tests.bat
if errorlevel 1 goto tests_failed
git push origin
git push github
git tag %1
git push origin %1
git push github %1
goto end

:tests_failed
echo Some tests failed, please ensure no tests fail before deploying.

:uncommitted_changes
echo There are unstaged or uncommitted_changes.

:version_issue
echo Version issues need to be resolved first.

:end
