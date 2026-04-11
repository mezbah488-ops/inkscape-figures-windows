@echo off
setlocal
set SD=%~dp0
:: CHANGE THIS TO 'py' TO USE THE CORRECT VERSION
set PY=python

if "%1"=="" goto usage
if "%1"=="init"  goto init
if "%1"=="start" goto start
if "%1"=="new"   goto new
if "%1"=="edit"  goto edit
if "%1"=="list"  goto list
if "%1"=="stop" goto stop
goto usage

:init
echo [fig] Initialising project in %CD%
if not exist figures mkdir figures
(
echo @echo off
echo for %%%%f in ^(*.tex^) do set T=%%%%f
echo if "%%T%%"=="" ^(echo [error] No .tex file found. ^& pause ^& exit /b^)
echo echo [fig] Watching: %%T%%
echo start /min "Inkscape-Opener" cmd /c %PY% "%SD%inkscape_figures.py" watch "%%T%%"
echo start /min "SVG-Exporter"    cmd /c %PY% "%SD%watch_figures.py" figures
) > start.bat
echo [fig] Created start.bat
echo.
echo Next steps:
echo   1. Add  \usepackage{incfig}  to your .tex preamble
echo   2. Run  fig start  (or double-click start.bat)
echo   3. Type  \incfig{name}  in your .tex and save
goto end

:start
if not exist start.bat (echo [fig] Run 'fig init' first. & goto end)
call start.bat
goto end

:new
if "%2"=="" (echo Usage: fig new ^<name^> & goto end)
for %%f in (*.tex) do set T=%%f
if "%T%"=="" (echo [fig] No .tex file found. & goto end)
%PY% "%SD%inkscape_figures.py" create "%T%" "%2"
goto end

:edit
if "%2"=="" (echo Usage: fig edit ^<name^> & goto end)
for %%f in (*.tex) do set T=%%f
if "%T%"=="" (echo [fig] No .tex file found. & goto end)
%PY% "%SD%inkscape_figures.py" edit "%T%" "%2"
goto end

:list
if not exist figures (echo [fig] No figures\ folder. & goto end)
echo. & echo Figures in this project: & echo.
set C=0
for %%f in (figures\*.svg) do (set /a C+=1 & echo    %%~nf)
if %C%==0 echo    (none yet)
echo.
goto end

:stop
echo [fig] Stopping watchers...
taskkill /f /im python.exe /fi "windowtitle eq Inkscape-Opener*" >nul 2>&1
taskkill /f /im python.exe /fi "windowtitle eq SVG-Exporter*" >nul 2>&1
wmic process where "commandline like '%%inkscape_figures.py%%'" delete >nul 2>&1
wmic process where "commandline like '%%watch_figures.py%%'" delete >nul 2>&1
echo [fig] Done.
goto end

:usage
echo.
echo  fig - Inkscape Figures workflow manager
echo.
echo    fig init          Initialise current folder as a LaTeX project
echo    fig start         Start both file watchers
echo    fig new  ^<name^>   Create + open a new figure in Inkscape
echo    fig edit ^<name^>   Open an existing figure in Inkscape
echo    fig list          List figures in this project
echo.
goto end

:end
endlocal
