cd %~dp0
if not exist "..\app\" (mkdir ..\app\)
pyinstaller -F ../main.py -p ../src/MCT_Tools.py -p ../src/MCT_Transform.py -p ../src/PDF_Merge_Process.py -p ../src/Image_Process.py -i ../MCT.ico
rename dist\* MCT.exe
move dist\* .
rd build dist /S /Q
del *.spec
move MCT.exe ..\app\
exit