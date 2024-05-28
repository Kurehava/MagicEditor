from os import system
from sys import exit
from platform import system as psystem
from time import sleep
from subprocess import Popen, PIPE

import src.Image_Process as Image_Process
import src.MCT_Tools as MCT_Tools
import src.PDF_Merge_Process as PDF_Merge_Process
import src.PDF_Secure_Process as PDF_Secure_Process
import src.PDF_Tools_Process as PDF_Tools_Process


def NAVIGATION(NI):
    if NI == 0:
        main_menu()
    elif NI in {1, 2, 3}:
        jump = Image_Process.navigation(NAVI=NI, config=config)
        if jump is not bool:
            NAVIGATION(jump)
    elif NI == 4:
        PDF_Merge_Process.entry(NI, config)
    elif NI in {"E", "e"}:
        exit(0)


"""    elif NI == 5:
        PDF_Tools_Process.entry()
    elif NI == 6:
        PDF_Secure_Process.entry()"""


def MCTHelp():
    content = "帮助：\n" \
              "1.只需要按照屏幕上显示的操作就好了\n" \
              "  选项是数字就输入数字\n" \
              "  是英文就输入英文。\n\n" \
              "2.源码全平台共通\n" \
              "  打包脚本在 create_app 目录下\n" \
              "  linux需要直接使用源码\n\n" \
              "3.直接使用源码的情况下\n" \
              "  请直接执行入口文件 mian.py.\n" \
              "  直接使用源码之前，请安装python依赖\n" \
              "  python3.x -m pip install -r requirements.txt\n\n" \
              "4.为了安全起见\n" \
              "  本脚本不会自动进行版本更新\n" \
              "  可以在以下的URl获取到最新的源码。\n\n" \
              "https://github.com/Kurehava/IMG-PDF-Conversion-Merger-Tool\n"
    system(CLEAR)
    print(content)
    input("输入回车返回主菜单")


def main_menu():
    try:
        while True:
            NAVI_INDEX = MCT_Tools.input_checker(config, MENU, 'int', {'0', '1', '2', '3', '4', '5'}, re_rule=r'[0-5]')
            if NAVI_INDEX == 0:
                MCTHelp()
                continue
            else:
                break
        NAVIGATION(NAVI_INDEX)
    except KeyboardInterrupt:
        if OS_TYPE in {"Windows", "Linux"}:
            system(CLEAR)
            exit(0)
        elif OS_TYPE == "Darwin":
            # iTerm 无法用macos terminal退出命令正常退出
            if str(Popen("echo $TERM_PROGRAM", stdout=PIPE, shell=True).communicate()[0])[2:-3] != "Apple_Terminal":
                system(CLEAR)
                exit(0)
            else:
                system("osascript -e 'tell application \"Terminal\" to close first window' & exit")


if __name__ == '__main__':
    # 定义抬头和彩色信息
    VERSION = 'v0.1.2'
    AUTHER_ = 'KurehaSho'
    ERROR_P = '[\033[091mERROR\033[0m]'
    WARN__P = '[\033[093mWARN-\033[0m]'
    INFO__P = '[\033[092mINFO-\033[0m]'
    NAME__P = f'\033[095m{AUTHER_}\033[0m'

    #  Merger Conversion Tool
    title_p = "\033[42;30m Merger Conversion Tool \033[0m"
    auther_ = "\033[41;93m Powered by KurehaSho   \033[0m"

    # 分系统定义
    OS_TYPE = psystem()
    if OS_TYPE in {'Linux', 'Darwin'}:
        CLEAR = 'clear'
        BACKSLASH = '/'
        system("printf '\033[8;25;55t'")
        system(CLEAR)
    elif OS_TYPE == 'Windows':
        CLEAR = 'cls'
        BACKSLASH = '//'
        system("chcp 936")
        system("mode con cols=51 lines=25")
        system(CLEAR)
    else:
        print(f'{WARN__P}: 无法确定您的系统类型')
        print(f'{WARN__P}: 继续运行可能会不稳定')
        CLEAR = 'clear'
        BACKSLASH = '/'

    # 显示开始屏
    print(
        "\033[42;30mPart of GravityWallToolsDevelopmentLAB Project.\033[0;96m\033[33m\n"
        f"\033[41;93mMCT-Python Ver {VERSION} Powered by {AUTHER_}     \033[0;96m\n\033[33m"
    )
    merger = f" __  __                          \n" \
             f"|  \\/  | ___ _ __ __ _  ___ _ __ \n" \
             f"| |\\/| |/ _ \\ '__/ _` |/ _ \\ '__|\n" \
             f"| |  | |  __/ | | (_| |  __/ |   \n" \
             f"|_|  |_|\\___|_|  \\__, |\\___|_|   \n" \
             f"                  |___/       "

    conversion = "  ____                              _              \n" \
                 " / ___|___  _ ____   _____ _ __ ___(_) ___  _ __   \n" \
                 "| |   / _ \\| '_ \\ \\ / / _ \\ '__/ __| |/ _ \\| '_ \\ \n" \
                 "| |__| (_) | | | \\ V /  __/ |  \\__ \\ | (_) | | | |\n" \
                 " \\____\\___/|_| |_|\\_/ \\___|_|  |___/_|\\___/|_| |_| \n"

    tools = " _____           _ \n" \
            "|_   _|__   ___ | |\n" \
            "  | |/ _ \\ / _ \\| |\n" \
            "  | | (_) | (_) | |\n" \
            "  |_|\\___/ \\___/|_|"

    print(f'\033[96m{merger}\033[0m')
    print(f'\033[91m{conversion}\033[0m')
    print(f'\033[93m{tools}\033[0m')
    # sleep(3)
    input("\n按下回车进入工具...")

    # FORMAT LIST
    PIL_FORMAT_LIST = ['BMP', 'DIB', 'EPS', 'GIF', 'ICNS', 'ICO', 'IM', 'JPEG',
                       'MSP', 'PCX', 'PNG', 'PPM', 'SGI', 'TGA', 'TIFF', 'WEBP',
                       'XMB', 'PDF', 'JPG', 'JPEG2000', 'SPIDER', 'AVIF']

    # GLOBAL Var
    EXT = 'png'
    FILE_LIST = []
    mmsp_transform = ''

    # 定义导航要素

    # 选项词典
    SELECT_DICT = {
        1: '1 - 图片 ->图片 单转',
        2: '2 - 图片<->SVG  互转',
        3: '3 - 图片<->PDF  互转',
        4: '4 - PDF 合并',
        5: '5 - PDF 文件编辑',
    }

    # 菜单选项
    # TODO: 进度- 1，2，3，4 完成 5，6 未完成
    """MENU = f'{title_p}\n{auther_}\n' \
           f'图片PDF操作统合工具 {VERSION}\n' \
           '===========================\n' \
           f'\033[96m<>-图片格式转换\033[0m\n' \
           '   | 1-图片 ->图片 单转\n' \
           '   | 2-图片<->SVG  互转\n' \
           '   | 3-图片<->PDF  互转\n' \
           '\033[96m<>-PDF编辑\033[0m\n' \
           '   | 4-PDF合并\n' \
           '      |-纯PDF合并\n' \
           '      |-图片+PDF合并\n' \
           '      |-多页数文件部分合并\n' \
           '   | 5-PDF页面操作\n' \
           '      |-页面顺序调换\n' \
           '      |-页面替换\n' \
           '      |-提取页面\n' \
           '\033[96m<>-PDF安全\033[0m\n' \
           '   | 6-PDF文件加密解密\n' \
           '==========================='"""

    MENU = '\033[42;30mMerger Conversion Tool \nPowered by KurehaSho   \033[0m\n' \
           f'图片PDF操作统合工具 {VERSION}\n' \
           '===========================\n' \
           f'\033[96m<>-图片格式转换\033[0m\n' \
           '   | 1-图片 ->图片 单转\n' \
           '   | 2-图片<->SVG  互转\n' \
           '   | 3-图片<->PDF  互转\n' \
           '\033[96m<>-PDF编辑\033[0m\n' \
           '   | 4-PDF合并\n' \
           '      |-纯PDF合并\n' \
           '      |-图片+PDF合并\n' \
           '      |-多页数文件部分合并\n' \
           '\033[96m<>-帮助\033[0m\n' \
           '   | 0-帮助\n' \
           '\033[96m<>-退出\033[0m\n' \
           '   | Ctrl + C\n' \
           '===========================\n' \
           'v0.2.0 前瞻:\n' \
           '    @.增加PDF文件操作模块\n' \
           '    @.增加PDF文件解密模块\n' \
           '==========================='

    # 打包传递给子函数的参数
    config = [
        CLEAR,
        VERSION,
        SELECT_DICT,
        PIL_FORMAT_LIST,
        BACKSLASH,
        OS_TYPE
    ]

    # 开始导航
    while True:
        main_menu()

    # TODO区域
    # TODO: PDF插入
    # TODO: 检测PDF页数 如果超过一页 那么就提示是从那个范围或者哪一页或者是全部都合并
    # TODO: PDF处理 功能: 插入，删除, 页面调换
    # TODO: PDF1 2到4页合并
    # TODO: 应用新的菜单
