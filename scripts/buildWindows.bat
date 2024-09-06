
@SETLOCAL
@ECHO OFF

cd /d %~dp0\..

pip install -r requirements.txt
@REM Install game and create distribution directory
pyinstaller game_of_life.py
@REM Copy game icon svg
xcopy /Y /S /I _static dist\game_of_life\_internal\_static

@ENDLOCAL
