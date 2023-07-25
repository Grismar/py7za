@echo off
git add .
git commit -m %1
git push
call scripts/cleanup.bat
call scripts/build.bat
twine upload dist/*
call scripts/cleanup.bat
