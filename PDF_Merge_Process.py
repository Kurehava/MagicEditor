from os import path, system, makedirs, rename
from re import findall
from shutil import rmtree, copy
from time import sleep

from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter

from MCT_Tools import LibraryPathSplit as Lps
from MCT_Tools import input_checker, decrypt_pdf
from MCT_Tools import input_data_clean as idc
from MCT_Transform import Image2Image
from MCT_Transform import image_checker as mtic

# pip install PyCryptodome
# 必须要这个import, 可以不用，但是要有
# import Crypto
import Crypto

ERROR_P = '[\033[091mERROR\033[0m]'
WARN__P = '[\033[093mWARN-\033[0m]'
INFO__P = '[\033[092mINFO-\033[0m]'


def entry(NAVI, config):
    # 获得待合并文件路径
    pp_return = path_process(NAVI, config)
    if pp_return == "EXIT":
        return 0
    else:
        merger_path_list, merger_count, multi_pdf_flag, encrypted_file_pw = pp_return
    # 合并处理
    mpp_return = multi_pdf_process(merger_path_list, multi_pdf_flag, encrypted_file_pw, config, NAVI)
    if mpp_return == "Exit":
        return 0
    return 0


def path_process(NAVI, config):
    # 解包
    CLEAR, VERSION, SELECT_DICT, PIL_FORMAT_LIST, BACKSLASH, OS_TYPE = config

    PM_BANNER = '\033[42;30mMerger Conversion Tool \nPowered by KurehaSho   \033[0m\n'\
                f'合并转换统合工具 {VERSION}\n' \
                f'{SELECT_DICT[NAVI]} 模式\n' \
                '=================================\n' \
                '\033[93m请按顺序拖入图片或者PDF文件并回车\n' \
                '请每次只拖入一个文件！！\033[0m\n' \
                '=================================\n' \
                '输入 d+回车 删除上一个输入\n' \
                '输入 e+回车 开始合并\n' \
                '输入 b+回车 返回主菜单\n' \
                '================================='

    # 定义变量
    merger_path_list = []
    merger_count = 0
    multi_pdf_flag = 0
    encrypted_file_pw = {}
    pdf_pages = {}

    # 取得文件路径
    while True:
        # 清屏 显示抬头
        system(CLEAR)
        print(PM_BANNER)

        # 显示现在列表中的元素
        if merger_count != 0:
            mfp_count = 1
            # merger_path_list:
            # [0] : 0:单页面文件, 1:多页面文件, 2:图片文件
            # [1] : 文件路径
            # [2] : 页面范围
            # [2] : 0:默认为1, 1:默认为空, 2:默认为IMG
            for mfp in merger_path_list:
                sm, fp, ff = mfp
                fp = Lps(fp)
                if sm in {0, 1}:
                    if sm == 0:
                        print(f'\033[93m{mfp_count}\033[0m. 文件类型: PDF\n'
                              f'   是否多页: 单页文件\n'
                              f'   文件名称: {fp.file_name_ext()}\n'
                              f'   文件路径: {fp.root()}\n')
                    if sm == 1:
                        pages = pdf_pages[f"{fp.file_path}"]
                        print(f'\033[93m{mfp_count}\033[0m. 文件类型: PDF\n'
                              f'   是否多页: 多页文件({pages}页)\n'
                              f'   文件名称: {fp.file_name_ext()}\n'
                              f'   文件路径: {fp.root()}\n')
                else:
                    print(f'\033[93m{mfp_count}\033[0m. 文件类型: IMG\n'
                          f'   是否多页: 否, 图像文件\n'
                          f'   文件名称: {fp.file_name_ext()}\n'
                          f'   文件路径: {fp.root()}\n')
                mfp_count += 1

        # 读取路径，并删除两遍多余符号
        merger_path = input('>> ').strip('"').strip(' ').strip('\'')
        # merger_path = merger_path.replace('\\', '')

        # 判定输入是否为 d, e, 回车 功能性输入
        # TODO:直接输入e的情况进行报错
        if merger_path not in {'d', 'e', '', 'b'}:
            # 判定输入文件是否为PDF文件
            if not path.exists(merger_path):
                print(f'{ERROR_P}: {merger_path}')
                for countdown in range(3, 0, -1):
                    print(f'\r{WARN__P}: 路径不存在, 请{countdown}秒后重新输入', end='')
                    sleep(1)
                continue
            if Lps(merger_path).ext().upper() == 'PDF':
                # merger_file_path.append(merger_path)
                reader = PdfFileReader(merger_path)
                if reader.isEncrypted:
                    info_list = decrypt_pdf(merger_path, config)
                    if info_list is False:
                        continue
                    else:
                        Encrypted_fp, passwd, OBJ = info_list
                    reader.decrypt(passwd)
                    encrypted_file_pw[Encrypted_fp] = passwd
                if reader.getNumPages() > 1:
                    # multi_pdf_list.append(merger_path)
                    merger_path_list.append([1, merger_path, ''])
                    pdf_pages[merger_path] = reader.getNumPages()
                    multi_pdf_flag = 1
                else:
                    merger_path_list.append([0, merger_path, '1'])
                merger_count += 1
            # 文件不为PDF文件，按图片文件处理
            elif mtic(merger_path, 'PDFMerger'):
                # merger_file_path.append(merger_path)
                merger_path_list.append([2, merger_path, 'IMG'])
                merger_count += 1
            else:
                print(f'{ERROR_P}: {merger_path}')
                print(f'{ERROR_P}: 此文件不为标准图片文件')
                print(f'{ERROR_P}: 或者PDF文件')
                print(f'{ERROR_P}: 跳过')
                input("按下回车继续")
                continue
            # sleep(2)

        # 输入为d，删除列表中最后一个元素
        elif merger_path in {'d', 'D', 'ｄ'}:
            # merger_file_path.pop()
            merger_path_list.pop()
            merger_count -= 1

        # 输入为e，弹出循环
        elif merger_path in {'e', 'E', 'ｅ'}:
            if len(merger_path_list) == 0:
                print(f"{WARN__P}: 请先拖入文件再合并")
                for countdown in range(3, 0, -1):
                    print(f'\r{WARN__P}:{countdown}秒后返回', end='')
                    sleep(1)
                continue
            else:
                break

        # 输入为b，返回主菜单
        elif merger_path in {'B', 'b'}:
            return "EXIT"

        # 不符合上面任意一项 输入错误
        else:
            print(f'{ERROR_P}: {merger_path}')
            for countdown in range(3, 0, -1):
                print(f'\r{WARN__P}: 输入错误，请{countdown}秒后重新输入', end='')
                sleep(1)
    return [merger_path_list, merger_count, multi_pdf_flag, encrypted_file_pw]


def multi_pdf_process(merger_path_list, multi_pdf_flag, encrypted_file_pw, config, NAVI):
    # 解包
    CLEAR, VERSION, SELECT_DICT, PIL_FORMAT_LIST, BACKSLASH, OS_TYPE = config

    LAST_BANNER = '\033[42;30mMerger Conversion Tool \nPowered by KurehaSho   \033[0m\n'\
                  f'合并转换统合工具 {VERSION}\n' \
                  f'{SELECT_DICT[NAVI]} 模式\n' \
                  '========================================\n'

    # 确保保存，缓存路径
    path_temp = Lps(merger_path_list[0][1])
    save_path = f"{path_temp.root()}/MERGER_{path_temp.nr}.pdf"
    temp_path = f"{path_temp.root()}/TEMP_{path_temp.nr}"
    if not path.exists(temp_path):
        makedirs(temp_path)

    # 选择是合并部分还是全部合并
    select_input = 0

    if multi_pdf_flag == 1:
        content = '\033[42;30mMerger Conversion Tool \nPowered by KurehaSho   \033[0m\n'\
                  f'合并转换统合工具 {VERSION}\n' \
                  f'{SELECT_DICT[NAVI]} 模式\n' \
                  '========================================\n' \
                  '检测到合并文件列表中含有多页数PDF文件\n' \
                  '您是准备:\n' \
                  '1.直接合并所有文件\n' \
                  '2.合并多页数PDF文件的一部分页数\n' \
                  '========================================'
        select_input = input_checker(config, content, 'int', input_set={'1', '2'}, re_rule=r'[1-2]')

    # 如果选择直接合并所有文件

    # 初始化 merger_list
    # TODO:合并时如果有图片在合并列表中，看看是不是需要缩放图片的大小
    merger_list = PdfFileMerger()
    if select_input == 1 or multi_pdf_flag != 1:
        for fn_path in merger_path_list:
            lfp = Lps(fn_path[1])
            if lfp.ext().upper() != 'PDF':
                if not path.exists(f'{temp_path}/{lfp.file_name_ext()}'):
                    copy(fn_path[1], temp_path)
                    old_name = f'{temp_path}/{lfp.file_name_ext()}'
                    new_name = f'{temp_path}/{lfp.file_name_mix()}.{lfp.ext()}'
                    rename(old_name, new_name)
                    sp = Image2Image([new_name, temp_path], 'pdf', save_path_return=True)
                    # print(f"DEBUG-N-PDF:{mmsp_transform}")
                    # fn_path[1] = f'{mmsp_transform}'
                    reader = PdfFileReader(sp)
                else:
                    sp = Image2Image([fn_path[1], temp_path], 'pdf', save_path_return=True)
                    # print(f"DEBUG-Y-PDF:{mmsp_transform}")
                    # fn_path[1] = f'{mmsp_transform}'
                    reader = PdfFileReader(sp)
            else:
                reader = PdfFileReader(fn_path[1])
                if reader.isEncrypted:
                    passwd = encrypted_file_pw[f"{fn_path[1]}"]
                    reader.decrypt(passwd)
            merger_list.append(reader)
        # print(f"PDF-SAVE-PATH:{save_path}")
        try:
            merger_list.write(save_path)
            system(CLEAR)
            print(LAST_BANNER)
            lsp = Lps(save_path)
            print(f"{INFO__P}: 操作全部完成\n"
                  f"{INFO__P}: 文件保存完成\n"
                  f"{INFO__P}: 文件名:\n{' ' * 9}{lsp.file_name_ext()}\n"
                  f"{INFO__P}: 路径:\n{' ' * 9}{lsp.root()}")
            rmtree(temp_path)
            input("按下回车返回主菜单")
        except Exception as E:
            print(f"{ERROR_P}: 发生致命错误\n"
                  f"{ERROR_P}: Location PMP-0\n"
                  f"{ERROR_P}: ERROR in step last\n"
                  f"{ERROR_P}: May be can not write file\n"
                  f"{ERROR_P}: {E}\n"
                  f"{ERROR_P}: 请把上述错误截图\n"
                  f"{ERROR_P}: 发送给开发者\n")
            rmtree(temp_path)
            exit(0)

    # 如果选择合并多页数PDF文件的一部分页数
    elif select_input == 2:
        mpe_return = mutil_page_editor(merger_path_list, encrypted_file_pw, NAVI, config)
        if mpe_return == "EXIT":
            return "EXIT"
        input_save, merger_path_list = mpe_return
        write_list = PdfFileWriter()
        chk_count = 0
        for multi_data in merger_path_list:
            chk_count += 1
            # 分析页码范围
            if multi_data[2] == 'IMG':
                # temp_path
                tp = Lps(multi_data[1])
                if not path.exists(f'{temp_path}/{tp.file_name_ext()}'):
                    copy(multi_data[1], temp_path)
                    old_name = f'{temp_path}/{tp.file_name_ext()}'
                    new_name = f'{temp_path}/{tp.file_name_mix()}.{tp.ext()}'
                    rename(old_name, new_name)
                    sp = Image2Image([new_name, temp_path], 'pdf', save_path_return=True)
                    # multi_data[1] = f'{new_name.replace(new_name.split(".")[-1], "")}.pdf'
                    # multi_data[1] = f'{mmsp_transform}'
                else:
                    sp = Image2Image([multi_data[1], temp_path], 'pdf', save_path_return=True)
                    # multi_data[1] = f'{temp_path}/{ICTools.split_path(multi_data[1], 3)[1]}.pdf'
                    # multi_data[1] = f'{mmsp_transform}'
                reader = PdfFileReader(sp)
                if reader.isEncrypted:
                    passwd = encrypted_file_pw[f"{multi_data[1]}"]
                    reader.decrypt(passwd)
                write_list.addPage(reader.getPage(0))
                continue
            else:
                page_range_list = multi_data[2].split(",")
                reader = PdfFileReader(multi_data[1])
                if reader.isEncrypted:
                    passwd = encrypted_file_pw[f"{multi_data[1]}"]
                    reader.decrypt(passwd)
                for range_num in page_range_list:
                    if "-" in range_num:
                        first_index = int(range_num.split("-")[0]) - 1
                        second_index = int(range_num.split("-")[1]) - 1
                        if first_index > second_index:
                            pages_list = [pgs for pgs in range(first_index, second_index - 1, -1)]
                        else:
                            pages_list = [pgs for pgs in range(first_index, second_index + 1)]
                        for nn in pages_list:
                            write_list.addPage(reader.getPage(nn))
                    else:
                        write_list.addPage(reader.getPage(int(range_num) - 1))
        try:
            with open(save_path, "ab") as woa:
                write_list.write(woa)
            lsp = Lps(save_path)
            system(CLEAR)
            print(LAST_BANNER)
            print(f"{INFO__P}: 操作全部完成\n"
                  f"{INFO__P}: 文件保存完成\n"
                  f"{INFO__P}: 文件名:\n{' ' * 9}{lsp.file_name_ext()}\n"
                  f"{INFO__P}: 文件路径:\n{' ' * 9}{lsp.root()}")
            try:
                rmtree(temp_path)
            except NotADirectoryError:
                print()
                print(f"{WARN__P}: 缓存文件夹无法读取"
                      f"{WARN__P}: 请手动删除缓存文件夹"
                      f"{WARN__P}: 文件夹名:\n{' '*9}{temp_path}")
            input("按下回车返回主菜单")
        except Exception as E:
            print(f"{ERROR_P}: 发生致命错误\n"
                  f"{ERROR_P}: Location PMP-1\n"
                  f"{ERROR_P}: ERROR in step last\n"
                  f"{ERROR_P}: May be can not write file\n"
                  f"{ERROR_P}: {E}\n"
                  f"{ERROR_P}: 请把上述错误截图\n"
                  f"{ERROR_P}: 发送给开发者\n")
            try:
                rmtree(temp_path)
            except NotADirectoryError:
                print()
                print(f"{WARN__P}: 缓存文件夹无法读取"
                      f"{WARN__P}: 请手动删除缓存文件夹"
                      f"{WARN__P}: 文件夹名:\n{' ' * 9}{temp_path}")
            exit(0)


def mutil_page_editor(merger_path_list, encrypted_file_pw, NAVI, config):
    # 解包
    CLEAR, VERSION, SELECT_DICT, PIL_FORMAT_LIST, BACKSLASH, OS_TYPE = config

    # 变量定义
    history_count = 0
    input_save = []
    mm_help_flag = 0
    reinput_mode = False

    content = '\033[42;30mMerger Conversion Tool \nPowered by KurehaSho   \033[0m\n'\
              f'合并转换统合工具 {VERSION}\n' \
              f'{SELECT_DICT[NAVI]} 模式\n' \
              f'SUB: 多页数编辑模式' \
              '========================================\n'

    banner = '\033[42;30mMerger Conversion Tool \nPowered by KurehaSho   \033[0m\n'\
             f'合并转换统合工具 {VERSION}\n' \
             f'{SELECT_DICT[NAVI]} 模式\n' \
             f'SUB: 多页数编辑模式\n' \
             '=================================================\n' \
             '请注意，在不清楚输入规则或者初次使用的情况下\n' \
             '请务必输入 help 按下回车 查看输入规则'

    mm_help = '1.多个页码请用英文半角的逗号","隔开\n' \
              '2.连续页码请用英文半角的横杠"-"链接开始与结束页码\n' \
              '3.可以按照想要排列的顺序填写，合并时会按照当前输入顺序合并\n' \
              '4.输入 b 可以取消所有的输入返回主菜单\n' \
              '5.输入 s 可以跳过当前文件,跳过的文件将全页面合并\n' \
              '6.输入错了的情况下在最后可以重新进行输入' \
              '  输入 e+想要重新进行输入的序号 可以进行重新输入\n' \
              '  e.g 重新输入序号为1的文件的页码： e+1\n' \
              '整体输入例: 2,23,3,4-8,1\n' \
              '================================================\n'

    not_exists_path_list = []
    for index in range(len(merger_path_list)):
        if not path.exists(merger_path_list[index][1]):
            not_exists_path_list.append(merger_path_list[index][1])

    if len(not_exists_path_list) > 0:
        print(content)
        print(f"{WARN__P}: 存在失效目录\n"
              f"{WARN__P}: 原因可能是源文件移动\n"
              f"{WARN__P}: 取消此次操作\n")
        return "EXIT"

    multi_file_list = []
    for multi_file_path in merger_path_list:
        if multi_file_path[0] == 1:
            multi_file_list.append(multi_file_path[1])

    while True:
        # 取 multi_file_path
        try:
            # 取 history_count 值作为下标
            # 如果 index[0] = 1 那么就作为多页数文件加载
            # 否则就 history_count + 1 跳过该文件
            # 这样的话 只要history_count不变动
            # multi_file_path 就会一直是同值
            if merger_path_list[history_count][0] == 1:
                multi_file_path = merger_path_list[history_count][1]
            else:
                history_count += 1
                continue
        except IndexError:
            break

        # 初始化 reader
        reader = PdfFileReader(multi_file_path)
        if reader.isEncrypted:
            passwd = encrypted_file_pw[f"{multi_file_path}"]
            reader.decrypt(passwd)
        file_pages = reader.getNumPages()

        # banner
        system(CLEAR)
        print(banner)
        print(f"================================================\n")
        if mm_help_flag == 1:
            print(mm_help)
            mm_help_flag = 0
        print(f'请输入需要合并的页码\n'
              f'请注意！现在操作的文件信息: \n'
              f'页码范围:\n'
              f'   \033[93m1~{file_pages}\033[0m\n'
              f'文件名:\n'
              f'   \033[93m{Lps(multi_file_path).file_name_ext()}\033[0m \n'
              f'文件路径:\n'
              f'   \033[93m{Lps(multi_file_path).root()}\033[0m \n'
              )

        # 输入检测
        while True:
            page_range = input("请输入需要进行合并的页码范围:\n>> ").strip("'").strip("\"").strip(" ")
            if page_range == "help":
                mm_help_flag = 1
                break
            elif findall(r'[AC-RT-Zac-rt-z]', page_range):
                print('您输入的页码范围中含有英文字母, 请重新输入。\n'
                      '(页码范围中只能存在半角逗号(英文输入法逗号)与数字。)')
                continue
            elif findall(r'[^0-9A-Za-z,+-]', page_range):
                print('您输入的页码范围中含有非法符号, 请重新输入。\n'
                      '(页码范围中只能存在半角逗号(英文输入法逗号)与数字。)')
                continue
            else:
                break

        # 输入判定
        if mm_help_flag == 1:
            continue
        elif page_range in {'B', 'b'}:
            return "EXIT"
        elif page_range in {'S', 's'}:
            input_save.append([history_count, multi_file_path, f'1-{file_pages}'])
            merger_path_list[history_count][2] = f'1-{file_pages}'
            history_count += 1
        # elif "e+" in page_range and page_range <= len(str(file_pages)) + 2:
        #     reinput_mode = True
        else:
            input_save.append([history_count, multi_file_path, page_range])
            merger_path_list[history_count][2] = page_range
            history_count += 1

    # 确认阶段
    record_count = 1
    illegal_input = False
    input_record = ""
    reinput_mode = False
    continue_flag = False

    # banner
    while True:
        system(CLEAR)
        print(banner)
        print(f"=\033[96m全部操作文件\033[0m====================================")
        for all_file_output in merger_path_list:
            afo = Lps(all_file_output[1])
            print(f"\033[92m>> \033[0m文件名　: {afo.file_name_ext()}\n"
                  f"{' ' * 3}文件路径: {afo.root()}")
            record_count += 1
        print(f"=\033[96mPDF多页面操作文件\033[0m===============================")
        record_count = 1
        for record_check in input_save:
            tp = Lps(record_check[1])
            print(f"\033[93m{record_count}\033[0m. 文件范围: {record_check[2]}\n"
                  f"{' ' * 3}文件名　: {tp.file_name_ext()}\n"
                  f"{' ' * 3}文件路径: {tp.root()}")
            record_count += 1
        if illegal_input:
            print(f"================================================\n"
                  f"{WARN__P}: 您的输入{input_record}\n"
                  f"{WARN__P}: 有误，请重新输入")
            illegal_input = False
        print(f"================================================\n"
              f"e+序号+回车 可以进入重输入模式")

        # 输入检测
        input_check = idc("确认进行操作吗?[确认'Y'/放弃并返回主菜单'N'] >>")
        if "e+" in input_check:
            try:
                file_index = int(input_check.replace("e+", ''))
                if file_index <= len(input_save):
                    # 唯一可继续值
                    reinput_mode = True
                else:
                    continue_flag = True
            except ValueError:
                continue_flag = True
        elif input_check not in {'Y', 'y', 'N', 'n'}:
            continue_flag = True
        else:
            if input_check in {"Y", "y"}:
                # return
                return input_save, merger_path_list
            elif input_check in {"N", "n"}:
                return "EXIT"
            else:
                continue_flag = True

        if continue_flag:
            input_record = input_check
            illegal_input = True
            continue_flag = False
            continue

        if reinput_mode:
            # 设定定量
            PAGE_RANGE = int(input_check.replace("e+", ''))
            FILE_PATH = Lps(input_save[PAGE_RANGE - 1][1])
            FILE_RANGE = input_save[PAGE_RANGE - 1][2]
            illegal_input = False
            input_record = ""

            while True:
                # banner
                system(CLEAR)
                print(banner)
                print(f"================================================")
                print(f"\033[091m页码范围重输入模式\033[0m:\n"
                      f"\033[93m操作文件\033[0m: \033[96m{FILE_PATH.file_name_ext()} \033[0m\n"
                      f"\033[93m现在范围\033[0m: \033[96m{FILE_RANGE} \033[0m\n"
                      f"\033[93m文件序号\033[0m: \033[96m{PAGE_RANGE} \033[0m\n"
                      f"\033[091m请再三确认操作文件的信息!!!\033[0m\n"
                      f"================================================")
                if illegal_input:
                    print(f"{WARN__P}: 您的输入{input_record}\n"
                          f"{WARN__P}: 有误，请重新输入\n"
                          f"================================================")
                    illegal_input = False
                file_confirm = idc("确认对此文件进行操作吗?[确认输入'Y'/取消输入'N'] >>")

                # 输入判定
                if file_confirm not in {'Y', 'y', 'N', 'n'}:
                    input_record = file_confirm
                    illegal_input = True
                    continue
                else:
                    if file_confirm in {"N", "n"}:
                        break
                    elif file_confirm in {"Y", "y"}:
                        # 重新获取页码范围
                        while True:
                            new_page_range = idc("请输入新的文件页码范围:")
                            if findall(r'[A-Za-z]', new_page_range):
                                print('您输入的页码范围中含有英文字母, 请重新输入。\n'
                                      '(页码范围中只能存在半角逗号(英文输入法逗号)与数字。)')
                                continue
                            elif findall(r'[^0-9A-Za-z,]', new_page_range):
                                print('您输入的页码范围中含有非法符号, 请重新输入。\n'
                                      '(页码范围中只能存在半角逗号(英文输入法逗号)与数字。)')
                                continue
                            else:
                                break
                        input_save[PAGE_RANGE - 1][2] = new_page_range
                        merger_path_list[input_save[PAGE_RANGE - 1][0]][2] = new_page_range
                        break
                continue
