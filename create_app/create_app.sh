cd "$(dirname "${BASH_SOURCE[0]}")" || exit
if [ ! -d "../app/" ];then
  mkdir "../app/"
fi
pyinstaller -F ../main.py -p ../src/MCT_Tools.py -p ../src/MCT_Transform.py -p ../src/PDF_Merge_Process.py -p ../src/Image_Process.py -i ../MCT.ico
mv dist/* ../app/MCT
rm -r build dist *.spec
exit