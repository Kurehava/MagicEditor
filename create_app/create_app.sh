cd "$(dirname "${BASH_SOURCE[0]}")" || exit
if [ ! -d "../app/" ];then
  mkdir "../app/"
fi
pyinstaller -F ../main.py -p ../MCT_Tools.py -p ../MCT_Transform.py -p ../PDF_Merge_Process.py -p ../Image_Process.py -i ../MCT.ico
mv dist/* ../app/MCT
rm -r build dist *.spec
exit