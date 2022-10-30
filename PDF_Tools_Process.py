import base64
import re
from re import findall
from os import path, system, walk, makedirs, rename
from platform import system as psystem
from random import sample
from shutil import rmtree, copy
from string import ascii_letters, digits
from time import strftime, localtime, sleep

import svgwrite
import fitz
from PIL import Image, UnidentifiedImageError
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

from MCT_Tools import input_data_clean as idc
from MCT_Tools import multiple_file_split as mfs
from MCT_Tools import input_checker as ic
from MCT_Tools import LibraryPathSplit as Lps
from MCT_Tools import decrypt_pdf

ERROR_P = '[\033[091mERROR\033[0m]'
WARN__P = '[\033[093mWARN-\033[0m]'
INFO__P = '[\033[092mINFO-\033[0m]'


# TODO:PDF页面位置转换，提取，页面替换

class PTP:
    def __init__(self, NAVI, config):
        CLEAR, VERSION, SELECT_DICT, PIL_FORMAT_LIST, BACKSLASH, OS_TYPE = config
        self.config = config
        self.NAVI = NAVI
        self.CLEAR = CLEAR
        self.VERSION = VERSION
        self.SELECT_DICT = SELECT_DICT
        self.PIL_FORMAT_LIST = PIL_FORMAT_LIST
        self.BACKSLASH = BACKSLASH
        self.OS_TYPE = OS_TYPE
        self.head = '\033[42;30mMerger Conversion Tool \nPowered by KurehaSho   \033[0m\n' \
                    f'合并转换统合工具 {self.VERSION}\n' \
                    f'{self.SELECT_DICT[self.NAVI]} 模式\n' \
                    '==========================\n'

    def entry(self):
        temp = PTP(self.NAVI, self.config)
        # 选择项目
        method_select = temp.method_select()
        if method_select == 5:
            return 0

        # 输入路径
        pdf_path = temp.get_pdf_path()

        # 解包PDF
        passwd, reader = temp.pdf_decrypt(pdf_path)

        # 操作PDF
        if method_select == 1:
            temp.page_switching(pdf_path, passwd)
        elif method_select == 2:
            temp.page_extraction()
        elif method_select == 3:
            temp.page_replacement()
        elif method_select == 4:
            temp.page_insert()

    def get_pdf_path(self):
        content = '请拖入一个文件:\n'
        not_pdf_flag = True
        while True:
            system(self.CLEAR)
            print(f"{self.head}")
            # pdf_path = idc(content) if self.OS_TYPE == "Windows" else mfs(content, self.config)
            if self.OS_TYPE == "Windows":
                pdf_path = idc(content)
                if Lps(pdf_path).ext().upper() != "PDF":
                    not_pdf_flag = False
            else:
                pdf_path = mfs(content, self.config)
                file_list, fail_list = pdf_path
                if len(file_list) > 1:
                    pdf_path = file_list[0]
                    print(f"{WARN__P}: 检测到您输入了多条目\n"
                          f"{WARN__P}: 按照要求我们取第一条目录")
                    if Lps(pdf_path).ext().upper() != "PDF":
                        not_pdf_flag = False
                    else:
                        break
            if not not_pdf_flag:
                print(f'{WARN__P}: 拖入文件不为PDF文件'
                      f'{WARN__P}: 请拖入PDF文件')
                for tc in range(3, 0, -1):
                    print(f"请在{tc}秒后重新拖入文件")
                    sleep(1)
                not_pdf_flag = True
                continue
        return pdf_path

    def method_select(self):
        select = f"1.PDF文件页面顺序调换\n" \
                 f"2.PDF文件页面提取\n" \
                 f"3.PDF文件页面替换\n" \
                 f"4.PDF文件页面插入\n" \
                 f"5.返回主菜单"
        return ic(self.config,
                  self.head + select,
                  "int",
                  {'1', '2', '3', '4', '5'},
                  all_num=True
                  )

    def pdf_decrypt(self, pdf_path):
        # 显示提示信息 基础信息获得
        passwd = ''
        reader = PdfFileReader(pdf_path)
        if reader.isEncrypted:
            pdf_path, passwd, reader = decrypt_pdf(pdf_path, self.config)
        return passwd

    def page_switching(self, pdf_path, passwd):
        reader = PdfFileReader(pdf_path)
        reader.decrypt(passwd)
        file_info = Lps(pdf_path)
        warning_flag = False
        warning_msg = ''
        switched_page_range = ''
        switching_page_range = ''

        input_flag = True
        input_msg_1 = "请输入被调换页面的页数或范围:\n" \
                      "(范围的起始用英文'-'进行连接)\n" \
                      "(2到5页的输入例为: 2-5)\n"
        input_msg_2 = "请输入调换页面的页数或范围:\n" \
                      "(范围的起始用英文'-'进行连接)\n" \
                      "(2到5页的输入例为: 2-5)\n"

        while True:
            system(self.CLEAR)
            print(self.head)
            content = f"{INFO__P}: 文件名：\n" \
                      f"{' ' * 9}{file_info.file_name_ext()}\n" \
                      f"{INFO__P}: 文件路径：\n" \
                      f"{' ' * 9}{file_info.root()}\n" \
                      f"{INFO__P}: 文件页数:\n" \
                      f"{' ' * 9}{reader.getNumPages()}页\n" \
                      f"==========================\n"
            if warning_flag:
                print(f'{warning_msg}==========================')
                warning_flag = False
            print(f'{content}')

            # 获得输入
            if input_flag:
                page_range = idc(input_msg_1)
            else:
                switched_page_range = page_range
                page_range = idc(input_msg_2)

            # 判定输入是否合法
            if findall(r'[A-Za-z]', page_range):
                warning_msg = f'{WARN__P}: 您的输入包含字母\n' \
                              f'{WARN__P}: 请重新输入\n'
                warning_flag = True
                continue
            elif findall(r'[^0-9A-Za-z-]', page_range):
                warning_msg = f'{WARN__P}: 您的输入包含非法字符\n' \
                              f'{WARN__P}: 请重新输入'
                warning_flag = True
                continue
            elif page_range is None:
                warning_msg = f'{WARN__P}: 您的输入为空\n' \
                              f'{WARN__P}: 请重新输入'
                warning_flag = True
                continue
            elif not input_flag:
                switching_page_range = page_range
                break
            else:
                input_flag = False
                continue

        warning_flag = False
        warning_msg = ''
        while True:
            system(self.CLEAR)
            print(self.head)
            info_content = f"{INFO__P}: 您输入的被调换页面为:\n" \
                           f"{' ' * 9}{switched_page_range}\n" \
                           f"{INFO__P}: 您输入的调换页面为:\n" \
                           f"{' ' * 9}{switching_page_range}\n" \
                           f"==========================\n"
            if warning_flag:
                print(f'{warning_msg}==========================')
                warning_flag = False
            print(info_content)
            confirm_select = idc("确认无误请按回车进行调换, 输入 e+回车 进行重输入")
            if findall(r'[^ Ee+]', confirm_select):
                warning_msg = f'{WARN__P}: 您的输入有误\n' \
                              f'{WARN__P}: 请重新输入'
                warning_flag = True
                continue
            elif confirm_select in {'E', 'e'}:
                temp = PTP(self.NAVI, self.config)
                ps_return = temp.page_switching(pdf_path, passwd)
                return ps_return
            else:
                break

        # TODO: 按照输入的页码进行替换页面

        return True

    def page_extraction(self):
        pass

    def page_replacement(self):
        pass

    def page_insert(self):
        pass
