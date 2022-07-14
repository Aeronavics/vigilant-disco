@ECHO ON
SET srcRoot=%~dp0
SET targetRoot=%AppData%\Autodesk\Autodesk Fusion 360\API
ECHO Creating hardlinks...

FOR /D %%A IN ("%srcRoot%\Scripts\*") DO (
	MKLINK /D "%TargetRoot%\Scripts\%%~NA" "%%~A"
	)

FOR /D %%A IN ("%srcRoot%\Addins\*") DO (
	MKLINK /D "%TargetRoot%\Addins\%%~NA" "%%~A"
	)

PAUSE
EXIT
