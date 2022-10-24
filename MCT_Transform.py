import base64
from os import path, makedirs, remove

import fitz
import svgwrite
import pillow_avif
from PIL import Image, UnidentifiedImageError
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

from MCT_Tools import LibraryPathSplit as Lps
from MCT_Tools import decrypt_pdf

ERROR_P = '[\033[091mERROR\033[0m]'
WARN__P = '[\033[093mWARN-\033[0m]'
INFO__P = '[\033[092mINFO-\033[0m]'


def image_checker(file_path, func_name):
    """
    检查画像文件是否为正常画像文件

    Args:
        file_path(str): 文件路径
        func_name(str): 函数名,l.

    Returns:
        bool: True/False 返回正常或不正常
    """
    try:
        Image.open(file_path).verify()
    except FileNotFoundError as FNFE:
        print(f'{ERROR_P}: {func_name}')
        print(f'{ERROR_P}: {FNFE}')
        print(f'{ERROR_P}: {file_path}')
        print(f'{ERROR_P}: 无法找到指定文件.')
        return False
    except UnidentifiedImageError as PUIE:
        print(f'{ERROR_P}: {func_name}')
        print(f'{ERROR_P}: {PUIE}')
        print(f'{ERROR_P}: {file_path}')
        print(f'{ERROR_P}: 文件不为支持的类型.')
        return False
    except ValueError as VE:
        print(f'{ERROR_P}: {func_name}')
        print(f'{ERROR_P}: {VE}')
        print(f'{ERROR_P}: If the mode is not "r".')
        print(f'{ERROR_P}: If a StringIO instance is used for fp.')
        print(f'{ERROR_P}: 给参错误，请反馈开发者.')
        return False
    except TypeError as TE:
        print(f'{ERROR_P}: {func_name}')
        print(f'{ERROR_P}: {TE}')
        print(f'{ERROR_P}: If formats is not None, a list or a tuple.')
        print(f'{ERROR_P}: 给参错误，请反馈开发者.')
        return False
    return True


# def Image2Image(file_path, save_path=None, ext='png'):
def Image2Image(fp, ext='png', save_path_return=False):
    """
    图片格式转换

    Args:
        fp(list): 文件路径，保存路径(可为空)
        # file_path(str): 文件路径
        # save_path(str): 保存路径(可无)
        ext(str): 转换目标文件类型
        save_path_return: 返回保存路径

    Returns:
        bool: 返回成功失败状态
    """
    (file_path, save_path) = fp
    if image_checker(file_path, 'image_changer'):
        file_path = Lps(file_path)
        if save_path is None:
            save_path = f'{file_path.root_file_name_mix()}.{ext}'
            # save_path = f'{file_path.root()}/MCT_{file_path.nr}/{file_path.no_ext_mix()}.{ext}'
        else:
            save_path = f'{save_path}/{file_path.file_name_mix()}.{ext}'
            # save_path = f'{save_path}/MCT_{file_path.nr}/{file_path.file_name_mix()}.{ext}'
    else:
        return False

    try:
        img = Image.open(file_path.file_path).convert('RGB')
        img.save(save_path)
    except ValueError as VE:
        # print(f"{ERROR_P}: {file_path.file_name_ext()} \033[91mFailed!\033[0m")
        print(f'{ERROR_P}: image_changer')
        print(f'{ERROR_P}: {VE}')
        print(f'{ERROR_P}: {ext}')
        print(f'{ERROR_P}: 不支持的转换类型.')
        return False
    except OSError as OSE:
        # print(f"{ERROR_P}: {file_path.file_name_ext()} \033[91mFailed!\033[0m")
        print(f'{ERROR_P}: image_changer')
        print(f'{ERROR_P}: {OSE}')
        print(f'{ERROR_P}: {save_path}')
        print(f'{ERROR_P}: 转换目标文件已存在或无法写入.')
        return False
    # print(f"{INFO__P}: {file_path.file_name_ext()} \033[92mSuccess!\033[0m")
    if save_path_return is True:
        return save_path
    return True


# def SVG2image(file_path, save_path=None, ext='png'):
def SVG2image(fp, ext='png'):
    """
    SVG文件转图像文件

    Args:
        fp(list): 文件路径，保存路径(可为空)
        # file_path(str): 文件路径
        # save_path(str): 保存路径(可无)
        ext(str): 转换目标文件类型

    Returns:
        bool: 返回成功失败状态
    """
    (file_path, save_path) = fp

    # 使用svg2rlg尝试读取文件来确定文件是否为正常SVG文件
    file_path = Lps(file_path)
    # print(file_path.file_path)
    drawing = svg2rlg(file_path.file_path)
    if drawing is None:
        print(f'{ERROR_P}: SVG2image')
        print(f'{ERROR_P}: {file_path}')
        print(f'{ERROR_P}: 读取源文件失败.')
        print(f'{ERROR_P}: 请确保源文件为SVG文件.')
        return False
    else:
        # 预定义保存路径
        if save_path is None:
            save_path = f'{file_path.root_file_name_mix()}.{ext}'
        else:
            save_path = f'{save_path}/{file_path.file_name_mix()}.{ext}'

    # 尝试写入目标文件
    try:
        renderPM.drawToFile(drawing, save_path, fmt=ext.upper(), dpi=2500)
    except Exception as E:
        print(f'{ERROR_P}: SVG2image')
        print(f'{ERROR_P}: {E}')
        print(f'{ERROR_P}: 尝试写入目标文件时错误.')
        # print(f"{ERROR_P}: {file_path.file_name_ext()} \033[91mFailed!\033[0m")
        return False

    # 返回成功
    # print(f"{INFO__P}: {file_path.file_name_ext()} \033[92mSuccess!\033[0m")
    return True


# def Image2SVG(file_path, save_path=None):
def Image2SVG(fp):
    """
    转换图片格式为SVG

    Args:
        fp(list): 文件路径，保存路径(可为空)
        # file_path(str): 文件路径
        # save_path(str): 保存路径

    Returns:
        bool: 返回成功失败状态
    """

    # 预定义保存路径与后缀名
    (file_path, save_path) = fp

    if image_checker(file_path, 'image_changer'):
        file_path = Lps(file_path)
        if save_path is None:
            save_path = f'{file_path.root_file_name_mix()}.svg'
        else:
            save_path = f'{save_path}/{file_path.file_name_mix()}.svg'
    else:
        return False
    ext = file_path.ext()

    # print(f'DEBUG: save_path - {save_path}')
    # 尝试读取源文件
    try:
        with open(file_path.file_path, 'rb') as fp:
            img = base64.b64encode(fp.read())
    except FileNotFoundError as FNFE:
        print(f'{ERROR_P}: Image2SVG')
        print(f'{ERROR_P}: {FNFE}')
        print(f'{ERROR_P}: 没有找到指定文件.')
        return False
    except UnicodeDecodeError as UDE:
        print(f'{ERROR_P}: Image2SVG')
        print(f'{ERROR_P}: {UDE}')
        print(f'{ERROR_P}: 不是能够被utf-8解码的文件.')
        return False

    # 初始化SVG然后写入
    try:
        dwg = svgwrite.Drawing(save_path)
        dwg.add(dwg.image(f'data:image/{ext};base64,' + img.decode("ascii"), size=(800, 800)))
        dwg.save()
    except Exception as E:
        # print(f"{ERROR_P}: {file_path.file_name_ext()} \033[91mFailed!\033[0m")
        print(f'{ERROR_P}: Image2SVG')
        print(f'{ERROR_P}: {E}')
        print(f'{ERROR_P}: 尝试写入SVG文件时错误.')
        return False

    # 返回正常
    # print(f"{INFO__P}: {file_path.file_name_ext()} \033[92mSuccess!\033[0m")
    return True


# def PDF2Image(file_path, ext, save_path=None):
def PDF2Image(fp, ext, config):
    """
    PDF转图像文件

    Args:
        fp(list): 文件路径，保存路径(可为空)
        # file_path (str): 文件路径
        # save_path (str): 保存路径
        ext (str): 转换文件类型
        config: 全局配置文件

    Returns:
        Bool (Bool): 返回成功与否
    """
    zoom_x, zoom_y, rotation_angle = 5, 5, 0

    (file_path, save_path) = fp
    temp_clear = False

    file_path = Lps(file_path)
    if save_path is None:
        save_path = f"{file_path.root_file_name_mix()}"
    else:
        save_path = f"{save_path}/{file_path.file_name_mix()}"

    try:
        reader = PdfFileReader(file_path.file_path)
        if reader.isEncrypted:
            info_list = decrypt_pdf(file_path.file_path, config)
            reader.decrypt(info_list[1])
            pdf_writer = PdfFileWriter()
            pdf_writer.appendPagesFromReader(reader)
            temp_path = f"{file_path.root_file_name_mix()}.pdf"
            with open(temp_path, "ab") as tpo:
                pdf_writer.write(tpo)
            temp_clear = True
        else:
            temp_path = file_path.file_path
        doc = fitz.open(temp_path)
        if not path.exists(f"{save_path}"):
            makedirs(f"{save_path}")
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom_x, zoom_y))
            # pix.save(f"{file_path.no_ext_mix()}/page-{page.number + 1}.{ext}")
            # f'{file_path.root()}/MCT_{file_path.nr}/{file_path.no_ext_mix()}.{ext}'
            pix.save(f"{save_path}/page-{page.number + 1}.{ext}")
        doc.close()
        if temp_clear:
            remove(temp_path)
        # print(f"{INFO__P}: {file_path.file_name_ext()} \033[92mSuccess!\033[0m")
        return True
    except TypeError as TE:
        # print(f"{ERROR_P}: {file_path.file_name_ext()} \033[91mFailed!\033[0m")
        print(f'{ERROR_P}: PDF2Image')
        print(f'{ERROR_P}: {TE}')
        print(f'{ERROR_P}: 尝试打开文件时出错.')
        return False
    except FileNotFoundError as FNFE:
        # print(f"{ERROR_P}: {file_path.file_name_ext()} \033[91mFailed!\033[0m")
        print(f'{ERROR_P}: PDF2Image')
        print(f'{ERROR_P}: {FNFE}')
        print(f'{ERROR_P}: 找不到指定文件.')
        return False
    except fitz.EmptyFileError as fEFE:
        # print(f"{ERROR_P}: {file_path.file_name_ext()} \033[91mFailed!\033[0m")
        print(f'{ERROR_P}: PDF2Image')
        print(f'{ERROR_P}: {fEFE}')
        print(f'{ERROR_P}: 文件或路径为空.')
        return False
    except ValueError as VE:
        # print(f"{ERROR_P}: {file_path.file_name_ext()} \033[91mFailed!\033[0m")
        print(f'{ERROR_P}: PDF2Image')
        print(f'{ERROR_P}: {VE}')
        print(f'{ERROR_P}: 参数错误.')
        return False
    except fitz.FileDataError as fFDE:
        # print(f"{ERROR_P}: {file_path.file_name_ext()} \033[91mFailed!\033[0m")
        print(f'{ERROR_P}: PDF2Image')
        print(f'{ERROR_P}: {fFDE}')
        print(f'{ERROR_P}: 给定类型无效，或文件为空.')
        return False
