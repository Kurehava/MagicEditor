from getpass import getpass
from os import path, system, walk
from random import sample
from re import findall
from string import ascii_letters, digits
from time import strftime, localtime, sleep

from PyPDF2 import PdfFileReader, errors

ERROR_P = '[\033[091mERROR\033[0m]'
WARN__P = '[\033[093mWARN-\033[0m]'
INFO__P = '[\033[092mINFO-\033[0m]'


def input_checker(config, content, input_type, input_set=None, input_list=None, content_list=None, wrap_number=None,
                  content_continue=None, re_rule=None, input_content=None, all_num=False,
                  all_eng=False, num_eng=False, must_upper=False, must_lower=False):
    """
    输入检测函数

    Args:
        config(list): CLEAR, VERSION, DICE
        content(str): 抬头文字内容
        input_type(str): 输入内容输出时的类型
        input_set(set): 输入内容的判定集合
        input_list(list): 输入内容的判定列表
        content_list(list): 在content中循环出列表内容
        wrap_number(int): 循环到多少次进行换行
        content_continue(str): 显示指定的后半部分content内容
        re_rule(str): 判定输入内容是否合法时使用的正则规则(使用正常匹配规则,不要使用反规则)
        input_content(str): 输入时的引导语
        all_num(bool): 全部为数字
        all_eng(bool): 全部为字母
        num_eng(bool): 英数混合
        must_upper(bool): 匹配列表元素时使输入内容强制大写
        must_lower(bool): 匹配列表元素时使输入内容强制小写

    Returns:
        返回指定类型的输入内容,或者错误

    """
    # 解包config
    CLEAR, VERSION, SELECT_DICT, PIL_FORMAT_LIST, BACKSLASH, OS_TYPE = config

    # 检查多重指定正则
    chk = [all_num, all_eng, num_eng, re_rule]
    if chk.count(True) > 1:
        print(f'{ERROR_P}: input_checker \n'
              f'{ERROR_P}: 正则算法一次只能指定一种.\n')
        return False

    # 参数指定
    input_check_flag = 0
    select_input_his = ''

    while True:
        # 显示提示语 content > content_list > content_continue
        system(CLEAR)
        print(content)
        if content_list is not None:
            wrap_count = 0
            for cl in content_list:
                if wrap_count == wrap_number:
                    print(f"{cl} ")
                    wrap_count = 0
                else:
                    print(f"{cl} ", end="")
                    wrap_count += 1
            print()
        if content_continue is not None:
            print(content_continue)

        # 按照插旗返回值定义输入提示语
        if input_check_flag == 0:
            if input_content is not None:
                ic_input = input(f'{input_content} >> ').strip('"').strip(' ').strip('\'')
            else:
                ic_input = input('请输入 >> ').strip('"').strip(' ').strip('\'')
        elif input_check_flag == 1:
            ic_input = input(
                f'{WARN__P}: 您的输入 \033[31m{select_input_his}\033[0m 有误\n请重新输入 >> ').strip(
                '"').strip(' ').strip('\'')
        elif input_check_flag == 2:
            # num false
            pass
        elif input_check_flag == 3:
            # eng false
            pass
        elif input_check_flag == 4:
            # num eng
            pass
        else:
            print(f'{ERROR_P}: input_check_flag \n'
                  f'{ERROR_P}: Value False.\n')
            input_check_flag = 1
            continue

        # 判定是否符合re
        if re_rule is not None:
            if not findall(re_rule, ic_input):
                input_check_flag = 1
                select_input_his = ic_input
                continue

        if all_num is not False:
            if findall("[^0-9]", ic_input):
                input_check_flag = 2
                select_input_his = ic_input
                continue

        if all_eng is not False:
            if findall("[^A-Za-z]", ic_input):
                input_check_flag = 3
                select_input_his = ic_input
                continue

        if num_eng is not False:
            if findall("[^A-Za-z0-9]", ic_input):
                input_check_flag = 4
                select_input_his = ic_input
                continue

        # 判定输入值是否在集合内
        if must_upper is not False:
            if input_set is not None and ic_input.upper() not in input_set:
                input_check_flag = 1
                select_input_his = ic_input
            elif input_list is not None and ic_input.upper() not in input_list:
                input_check_flag = 1
                select_input_his = ic_input
            else:
                break
        elif must_lower is not False:
            if input_set is not None and ic_input.upper() not in input_set:
                input_check_flag = 1
                select_input_his = ic_input
            elif input_list is not None and ic_input.upper() not in input_list:
                input_check_flag = 1
                select_input_his = ic_input
            else:
                break
        elif input_set is not None and ic_input not in input_set:
            input_check_flag = 1
            select_input_his = ic_input
        elif input_list is not None and ic_input not in input_list:
            input_check_flag = 1
            select_input_his = ic_input
        else:
            break

    # 按照指定类型更改类型
    if input_type == 'int':
        ic_input = int(ic_input)
    elif input_type == 'float':
        ic_input = float(ic_input)

    # 输出输入值
    return ic_input


class LibraryPathSplit:
    def __init__(self, file_path):
        random_str = ''.join(sample(ascii_letters + digits, 2))
        now_time = strftime("%Y%m%d%H%M%S", localtime())
        nr = f'{now_time}_{random_str}'

        self.file_path = f"{file_path}"
        self.nr = nr

    def root(self):
        return path.split(str(self.file_path))[0]

    def ext(self):
        return path.splitext(path.split(self.file_path)[1])[1].split('.')[-1]

    def file_name_ext(self):
        return path.split(self.file_path)[1]

    def file_name(self):
        return path.splitext(path.split(self.file_path)[1])[0]

    def file_name_mix(self):
        return f"{path.splitext(path.split(self.file_path)[1])[0]}_{self.nr}"

    def root_file_name(self):
        return f'{path.split(self.file_path)[0]}/{path.splitext(path.split(self.file_path)[1])[0]}'

    def root_file_name_mix(self):
        return f'{path.split(self.file_path)[0]}/{path.splitext(path.split(self.file_path)[1])[0]}_{self.nr}'

    def all(self):
        temp = LibraryPathSplit(self.file_path)
        return [self.file_path,
                temp.root(),
                temp.ext(),
                temp.file_name_ext(),
                temp.file_name(),
                temp.file_name_mix(),
                temp.root_file_name(),
                temp.root_file_name_mix()]


def manual_path_split(file_path, config):
    """
        文件路径处理(Manual)

        Args:
            file_path (str): 文件路径
            config (list): config

        Returns:
            list: 0:file_path, 1:root, 2:file_name, 3:ext,
                  4:file_name_mix, 5:no_ext, 6:no_ext_mix
    """
    # 解包config
    CLEAR, VERSION, SELECT_DICT, PIL_FORMAT_LIST, BACKSLASH, OS_TYPE = config

    random_str = ''.join(sample(ascii_letters + digits, 2))
    now_time = strftime("%Y%m%d%H%M%S", localtime())
    nr = f'{now_time}_{random_str}'

    root = file_path.replace(file_path.split(BACKSLASH)[-1], '')
    file_name = file_path.replace(file_path.split(BACKSLASH)[-1].split('.')[-1], '')
    ext = file_name.split('.')[-1]

    file_name_mix = f'{file_name}_{nr}'
    no_ext = f'{root}/{file_name}'
    no_ext_mix = f'{no_ext}_{nr}'

    return [file_path, root, file_name, ext, file_name_mix, no_ext, no_ext_mix]


def multiple_file_split(content, config):
    """
    多文件终端拖入路径分离函数

    :return: file_list, fail_list
    """
    # 解包config
    CLEAR, VERSION, SELECT_DICT, PIL_FORMAT_LIST, BACKSLASH, OS_TYPE = config
    system(CLEAR)
    print(content)

    input_path = input('请拖入文件 >> ')
    file_list = []
    fail_list = []
    addr_start = -1
    addr_end = 0
    addr_flags = 0

    input_path = f'{input_path}/'
    for length in range(len(input_path)):
        if input_path[length] == '/' and addr_flags != 1:
            # print(f'DEBUG-flag-1:{addr_flags}::{length}->{addr_start}-{addr_end}')
            addr_flags = 1
            addr_start = length
        if input_path[length] == '.' and addr_flags == 1:
            # print(f'DEBUG-flag-2:{addr_flags}::{length}->{addr_start}-{addr_end}')
            addr_flags = 2
        if input_path[length:length + 2] == ' /' and addr_flags == 2:
            # print(f'DEBUG-flag-3:{addr_flags}::{length}->{addr_start}-{addr_end}')
            addr_flags = 3
            addr_end = length
        elif input_path[length:length + 2] == ' /' and addr_flags != 2:
            # print(f'DEBUG-flag-4:{addr_flags}::{length}->{addr_start}-{addr_end}')
            addr_start = 0
            addr_end = 0
            addr_flags = 0
        if addr_start != -1 and addr_end != 0 and addr_flags == 3:
            # print(f'DEBUG-flag-5:{addr_flags}::{length}->{addr_start}-{addr_end}')
            file_path = input_path[addr_start:addr_end]
            file_path = file_path.replace("\\", "")
            # print(f'DEBUG-file_path:{file_path}')
            if path.isfile(file_path) and len(file_path) > 10:
                file_list.append(file_path)
            else:
                fail_list.append(file_path)
            addr_start = 0
            addr_end = 0
            addr_flags = 0
    if not file_list:
        print(f'{ERROR_P}: multiple_file_split \n'
              f'{ERROR_P}: 没有检测到拖入文件.\n')
        input("按下回车返回主菜单")
        return False
    return file_list, fail_list


def folder_file_statistic(content, config):
    # 解包config
    CLEAR, VERSION, SELECT_DICT, PIL_FORMAT_LIST, BACKSLASH, OS_TYPE = config

    file_list = []
    fail_list = []

    system(CLEAR)
    print(content)

    INPUT_PATH = input('请拖入文件夹\n>> ').strip(r" ").strip(r"'").strip(r'"')
    if not path.isdir(INPUT_PATH):
        print(f'{WARN__P}: 您拖入的不为文件夹，请重新开始选择.')
        for n in range(2, 0, -1):
            print(f'\r{n}秒后重新选择.', end='')
            sleep(1)
        (file_list, fail_list) = folder_file_statistic(content, config)
    else:
        for root, dirs, files in walk(INPUT_PATH):
            for f in files:
                file_path = path.join(root, f)
                if path.isfile(file_path):
                    file_list.append(file_path)
                else:
                    fail_list.append(file_path)
    if len(file_list) == 0:
        print(f'{ERROR_P}: folder_file_statistic \n'
              f'{ERROR_P}: 文件夹内可用文件为空.\n')
        input("按下回车返回主菜单")
        return False
    return file_list, fail_list


def decrypt_pdf(fp, config):
    CLEAR, VERSION, SELECT_DICT, PIL_FORMAT_LIST, BACKSLASH, OS_TYPE = config

    banner = f"\033[093m===========================\033[0m \n" \
             f"{LibraryPathSplit(fp).file_name_ext()}\n" \
             f"为加密文件.\n" \
             f"请输入文件密码来继续操作。\n" \
             f"输入 e+回车 来跳过这个文件。 \n" \
             f"\033[093m===========================\033[0m\n"

    reader = PdfFileReader(fp)
    reader.decrypt("")
    try:
        reader.getNumPages()
        info_list = [fp, "", reader]
        return info_list
    except errors.PdfReadError:
        while True:
            system(CLEAR)
            print(banner)
            pw = getpass("请输入密码 \033[93m>\033[0m").strip(" ").strip("'").strip("\"")
            if pw in {"e", "E"}:
                return False

            reader.decrypt(pw)
            try:
                reader.getNumPages()
                info_list = [fp, pw, reader]
                return info_list
            except errors.DependencyError as eD:
                print(f"{ERROR_P}: {eD}")
                print(f"{ERROR_P}: 此文件加密方式不被支持"
                      f"{ERROR_P}: 自动跳过此文件"
                      f"{ERROR_P}: 请把此错误截图给开发者")
                return False
            except errors.PdfReadError as eP:
                if str(eP) == "File has not been decrypted":
                    print(f"{WARN__P}: 您的密码输入可能有误，")
                    for num in range(3, 0, -1):
                        print(f"\r请{num}s后重新输入.", end="")
                        sleep(1)
                    continue
                else:
                    print(f"{WARN__P}: 读取文件出现问题"
                          f"{WARN__P}: 自动跳过此文件"
                          f"{WARN__P}: 请稍后重新独立处理此文件")
                    return False


def input_data_clean(content):
    idc = input(content).strip(" ").strip("'").strip("\"")
    return idc
