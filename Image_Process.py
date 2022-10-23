import copy
from os import system, makedirs
from os.path import exists
from time import sleep

import MCT_Transform
from MCT_Tools import LibraryPathSplit as Lps
from MCT_Tools import folder_file_statistic as ffs
from MCT_Tools import input_checker as mtic
from MCT_Tools import multiple_file_split as mfs
from MCT_Tools import input_data_clean as idc

ERROR_P = '[\033[091mERROR\033[0m]'
WARN__P = '[\033[093mWARN-\033[0m]'
INFO__P = '[\033[092mINFO-\033[0m]'


def navigation(NAVI=None, config=None, jump=None):
    if type(jump) is int:
        return jump
    entry(NAVI, config)
    return 0


def entry(NAVI, config):
    # 解包config
    CLEAR, VERSION, SELECT_DICT, PIL_FORMAT_LIST, BACKSLASH, OS_TYPE = config

    # 获取转换目标文件类型与文件列表
    # EXT = ext(NAVI, config)
    # file_list, fail_list = file_input_process(NAVI, config)
    # POSITION = save_position(NAVI, config)
    EXT = ext(NAVI, config)
    if EXT == "EXIT":
        return 0

    while True:
        status_list = file_input_process(NAVI, config)
        if status_list == "EXIT":
            return 0
        elif status_list == "WHILE":
            print(f"{ERROR_P}: 文件路径不存在")
            for countdown in range(3, 0, -1):
                print(f'\r{ERROR_P}:请{countdown}秒后重新输入', end='')
                sleep(1)
            continue
        elif type(status_list) is list:
            file_list, fail_list = status_list
            break
        else:
            print(f"{ERROR_P}: 没有检测到任何输出"
                  f"{ERROR_P}: 重新进入文件拖入阶段")
            for countdown in range(3, 0, -1):
                print(f'\r{WARN__P}:{countdown}秒后返回', end='')
                sleep(1)
            continue

    POSITION = save_position(NAVI, config)
    if POSITION == 3:
        return 0

    # 开始转换步骤
    system(CLEAR)
    banner = (
        '\033[42;30mMerger Conversion Tool \nPowered by KurehaSho   \033[0m\n'
        f'合并转换统合工具 {VERSION}\n'
        f'{SELECT_DICT[NAVI]} 模式\n'
        '===========================\n'
    )
    print(banner)

    false_count = 0
    error_list = []

    if POSITION == 1:
        temp_path = file_list[0]
        temp_path = Lps(temp_path)
        SAVE_PATH = f"{temp_path.root()}/MCT_{EXT.upper()}_{temp_path.nr}/"
        if not exists(SAVE_PATH):
            makedirs(SAVE_PATH)
    else:
        SAVE_PATH = None

    # TODO: 当选择保存在同一个目录下个各个文件目录下的时候的路径问题
    continue_count = 0
    output_list = []
    for f_p in file_list:
        # 后缀名，文件路径，保存路径指定
        fp_ext = Lps(f_p).ext()
        if fp_ext.upper() not in PIL_FORMAT_LIST and fp_ext.upper() not in {"SVG", "svg"}:
            continue_count += 1
            continue
        fp = [f_p, SAVE_PATH]

        if NAVI == 1:
            if fp_ext in {'PDF', 'pdf'}:
                # TODO:加上PDF转图片，多页PDF全部转图片
                # 如果指定EXT为JPG或PNG直接转就行
                # 不是以上两种格式的话，先转成以上两种格式
                # 再转成其他的格式
                if not MCT_Transform.PDF2Image(fp, EXT, config):
                    error_list.append(fp[0])
                    false_count += 1
                    print(f'{ERROR_P}: NAVI - 1\n'
                          f'{ERROR_P}: change2image\n'
                          f'{ERROR_P}: sub: image_change\n'
                          f'{ERROR_P}: EXT: PDF => {EXT}\n'
                          f'{ERROR_P}: {fp[0]}\n'
                          f'{ERROR_P}: 文件转换发生错误.')
                    input("按下回车继续后面的转换")
                    output_list.append([fp[0], False])
                else:
                    output_list.append([fp[0], True])
            else:
                if not MCT_Transform.Image2Image(fp, ext=EXT):
                    error_list.append(fp[0])
                    false_count += 1
                    print(f'{ERROR_P}: change2image\n'
                          f'{ERROR_P}: sub: image_change\n'
                          f'{ERROR_P}: {fp[0]}\n'
                          f'{ERROR_P}: 文件转换发生错误.')
                    input("按下回车继续后面的转换")
                    output_list.append([fp[0], False])
                else:
                    output_list.append([fp[0], True])
        elif NAVI == 2:
            if fp_ext in {'SVG', 'svg'}:
                if not MCT_Transform.SVG2image(fp, ext=EXT):
                    error_list.append(fp[0])
                    false_count += 1
                    print(f'{ERROR_P}: change2image\n'
                          f'{ERROR_P}: sub: SVG2Image\n'
                          f'{ERROR_P}: {fp[0]}\n'
                          f'{ERROR_P}: 文件转换发生错误.')
                    input("按下回车继续后面的转换")
                    output_list.append([fp[0], False])
                else:
                    output_list.append([fp[0], True])
            else:
                if not MCT_Transform.Image2SVG(fp):
                    error_list.append(fp[0])
                    false_count += 1
                    print(f'{ERROR_P}: change2image\n'
                          f'{ERROR_P}: sub: Image2SVG\n'
                          f'{ERROR_P}: {fp[0]}\n'
                          f'{ERROR_P}: 文件转换发生错误.')
                    input("按下回车继续后面的转换")
                    output_list.append([fp[0], False])
                else:
                    output_list.append([fp[0], True])
        elif NAVI == 3:
            if fp_ext in {'PDF', 'pdf'}:
                if not MCT_Transform.PDF2Image(fp, EXT, config):
                    error_list.append(fp[0])
                    false_count += 1
                    print(f'{ERROR_P}: NAVI - 3\n'
                          f'{ERROR_P}: change2image\n'
                          f'{ERROR_P}: sub: image_change\n'
                          f'{ERROR_P}: EXT: PDF => {EXT}\n'
                          f'{ERROR_P}: {fp[0]}\n'
                          f'{ERROR_P}: 文件转换发生错误.')
                    input("按下回车继续后面的转换")
                    output_list.append([fp[0], False])
                else:
                    output_list.append([fp[0], True])
            else:
                if not MCT_Transform.Image2Image(fp, ext='PDF'):
                    error_list.append(fp[0])
                    false_count += 1
                    print(f'{ERROR_P}: change2image\n'
                          f'{ERROR_P}: sub: image_change\n'
                          f'{ERROR_P}: EXT: {EXT} => PDF\n'
                          f'{ERROR_P}: {fp[0]}\n'
                          f'{ERROR_P}: 文件转换发生错误.')
                    input("按下回车继续后面的转换")
                    output_list.append([fp[0], False])
                else:
                    output_list.append([fp[0], True])
        system(CLEAR)
        print(banner)
        if len(output_list) > 0:
            for output in range(len(output_list)):
                if output_list[output][1] is False:
                    print(f"{ERROR_P}: {Lps(output_list[output][0]).file_name_ext()} \033[91mFailed!\033[0m")
                else:
                    print(f"{INFO__P}: {Lps(output_list[output][0]).file_name_ext()} \033[92mSuccess!\033[0m")
    print()
    if false_count > 0 or len(fail_list) > 0 or continue_count > 0:
        print(f'{WARN__P}: 跳过执行 {continue_count} 个文件.')
        print(f'{WARN__P}: 文件转换发生 {false_count} 次错误.')
        print(f'{WARN__P}: 文件提取发生 {len(fail_list)} 次错误.')
        print(f'{INFO__P}: 正常文件转换全部完成.')
    else:
        print(f'{INFO__P}: 正常文件转换全部完成.')
    input('按下回车返回主菜单')
    navigation(jump=0)


def ext(NAVI, config):
    # 解包config
    CLEAR, VERSION, SELECT_DICT, PIL_FORMAT_LIST, BACKSLASH, OS_TYPE = config

    # 转换格式输入判定
    content = '\033[42;30mMerger Conversion Tool \nPowered by KurehaSho   \033[0m\n' \
              f'合并转换统合工具 {VERSION}\n' \
              f'{SELECT_DICT[NAVI]} 模式\n' \
              '========================================\n' \
              '支持的输出文件类型:'
    content_continue = '========================================\n' \
                       '注意: \n' \
                       '>> SVG,PDF互转模式时,此处文件类型设定将\n' \
                       '  适用到SVG,PDF转换为图像文件时使用。\n' \
                       '>> SVG格式转图片格式通常都会都不会很好,\n' \
                       '  所以不要轻易用SVG转换为图片格式。\n' \
                       '>> b+回车返回上级菜单\n' \
                       '========================================\n'
    input_content = "请输入转换格式"
    input_list = copy.copy(PIL_FORMAT_LIST)
    input_list.extend(["B", "b"])
    i_c = mtic(config, content, "str", input_list=input_list, content_list=PIL_FORMAT_LIST,
               content_continue=content_continue, input_content=input_content,
               all_eng=True, wrap_number=8, must_upper=True)

    # i_c输入检测
    if i_c in {"B", "b"}:
        return "EXIT"
    else:
        return i_c


def file_input_process(NAVI, config):
    # 解包config
    CLEAR, VERSION, SELECT_DICT, PIL_FORMAT_LIST, BACKSLASH, OS_TYPE = config

    file_list = []
    fail_list = []

    # 文件路径输入模式选择
    content = '\033[42;30mMerger Conversion Tool \nPowered by KurehaSho   \033[0m\n' \
              f'合并转换统合工具 {VERSION}\n' \
              f'{SELECT_DICT[NAVI]} 模式\n' \
              '================================\n' \
              '您是想要:\n' \
              '1.拖入单个或多个文件转换\n' \
              '2.拖入文件夹批量转换\n' \
              '3.返回主菜单\n' \
              '================================\n'\
              'Windows用户不能一次性拖入多个文件,\n'\
              '请先将多个文件保存在同一个文件夹中,\n'\
              '选择【2.拖入文件夹批量转换】\n'\
              '================================'
    select = mtic(config, content, 'int', {'1', '2', '3'}, re_rule=r'[1-3]')

    # 按照模式文件路径提取为list或者返回主菜单
    # TODO: return mfs or ffs is None, need to back main menu
    if select == 1:
        content_2 = '\033[42;30mMerger Conversion Tool \nPowered by KurehaSho   \033[0m\n' \
                    f'合并转换统合工具 {VERSION}\n' \
                    f'{SELECT_DICT[NAVI]} 模式\n' \
                    '==========================='
        if OS_TYPE == "Windows":
            system(CLEAR)
            print(content_2)
            path = idc("windows模式,请拖入单个文件 \n>>")
            if not exists(path):
                fail_list.append(path)
                return "WHILE"
            else:
                file_list.append(path)
        else:
            # file_list, fail_list = mfs(content_2, config)
            mfs_return = mfs(content_2, config)
            if mfs_return is False:
                return "EXIT"
            else:
                file_list, fail_list = mfs_return
    elif select == 2:
        content_2 = '\033[42;30mMerger Conversion Tool \nPowered by KurehaSho   \033[0m\n' \
                    f'合并转换统合工具 {VERSION}\n' \
                    f'{SELECT_DICT[NAVI]} 模式\n' \
                    '==========================='
        # file_list, fail_list = ffs(content_2, config)
        ffs_return = ffs(content_2, config)
        if ffs_return is False:
            return "EXIT"
        else:
            file_list, fail_list = ffs_return
    elif select == 3:
        # navigation(jump=0)
        return "EXIT"

    if file_list is None:
        print(f'{ERROR_P}: file_input_process error\n'
              f'{ERROR_P}: 没有检测到任何输入文件路径,\n'
              f'{ERROR_P}: 返回上一层菜单.\n'
              f'{INFO__P}: 您可以在上一层菜单选择返回主菜单.')
        input("按下回车继续")

    ff_list = [file_list, fail_list]
    return ff_list


def save_position(NAVI, config):
    # 解包config
    CLEAR, VERSION, SELECT_DICT, PIL_FORMAT_LIST, BACKSLASH, OS_TYPE = config
    content = '\033[42;30mMerger Conversion Tool \nPowered by KurehaSho   \033[0m\n' \
              f'合并转换统合工具 {VERSION}\n' \
              f'{SELECT_DICT[NAVI]} 模式\n' \
              '===========================\n' \
              '您是想要:\n' \
              '1.保存所有转换文件到同一个文件夹中\n' \
              '2.保存各个转换文件到各个文件源目录下\n' \
              '3.返回主菜单\n' \
              '===========================\n'
    select = mtic(config, content, "int", input_set={"1", "2", "3"}, re_rule=r'[1-3]')
    return select
