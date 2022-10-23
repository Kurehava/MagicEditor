cd %~dp0
pyinstaller -F ../main.py -p ../MCT_Tools.py -p ../MCT_Transform.py -p ../PDF_Merge_Process.py -p ../Image_Process.py -i ../MCT.ico
rename dist\* MCT.exe
move dist\* .
rd build dist /S /Q
del *.spec
move MCT.exe ..\app\
exit