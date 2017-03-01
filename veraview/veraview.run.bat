@echo off
setlocal

set VERAViewDir=%~dp0

rem ---------------------------------------------------------------------
rem - If you changed the path for your per-user Canopy environment setup,
rem - set the value of the CanopyUserDir variable to point to the User subdir
rem - under that path.
rem ---------------------------------------------------------------------
set CanopyUserDir=%userprofile%\AppData\Local\Enthought\Canopy\User


if exist "%CanopyUserDir%\python.exe" goto found
echo msgbox "Canopy installation not found.  Edit this script to set the CanopyUserDir variable." > %temp%\msg.vbs
call "%temp%\msg.vbs"
goto finished


:found
rem if "%PROCESSOR_ARCHITECTURE%" == "x86" goto x86
rem path=%VERAViewDir%bin\win64;%path%
rem goto launch
rem :x86
rem path=%VERAViewDir%bin\win32;%path%


rem :launch
set PYTHONPATH=%VERAViewDir%;%PYTHONPATH%
"%CanopyUserDir%\python" "%VERAViewDir%veraview.py" %1 %2 %3 %4 %5 %6 %7 %8 %9


:finished
endlocal
