# -*- coding: utf-8 -*-


import os
import pickle
import zipfile


def unzip_csv_folder(zip_path, file_name='data.zip'):
    """
    :param zip_path: str, 因子数据压缩包路径
    :return:
    解压缩因子数据压缩包，压缩包中尚未解压到目标文件夹中的文件将被解压
    """
    zip_file = zipfile.ZipFile(os.path.join(zip_path, file_name), "r")
    for name in zip_file.namelist():
        name = name.replace('\\', '/')
        # 检查文件夹是否存在,新建尚未存在的文件夹
        if name.endswith("/"):
            ext_dir = os.path.join(zip_path, name)
            if not os.path.exists(ext_dir):
                os.mkdir(ext_dir)
        # 检查数据文件是否存在，新建尚未存在的数据文件
        else:
            ext_filename = os.path.join(zip_path, name)
            ext_dir = os.path.dirname(ext_filename)
            if not os.path.exists(ext_dir):
                os.mkdir(ext_dir)
            if not os.path.exists(ext_filename):
                outfile = open(ext_filename, 'wb')
                outfile.write(zip_file.read(name))
                outfile.close()
    return


def pickle_dump_data(data, pkl_name, protocol=-1):
    """
    :param data: any type
    :param pkl_name: str, *.pkl
    :param protocol: int, optional, protocol in saving pickle
    :return:
    """
    files = open(pkl_name, 'wb')
    pickle.dump(data, files, protocol)
    files.close()
    return "pickle file {0:s} saved".format(pkl_name)


def pickle_load_data(pkl_name):
    """
    :param pkl_name: *.pkl
    :return: data saved in *.pkl
    """

    files = open(pkl_name, 'rb')
    data = pickle.load(files)
    files.close()
    return data
