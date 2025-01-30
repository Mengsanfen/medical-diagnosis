import os


def del_filedir(path):
    for file in os.listdir(path):
        res = os.path.join(path, file)
        print(res)  # 打印给定目录下的文件及文件夹
        if os.path.isfile(res):
            os.remove(res)
        else:
            if os.path.isdir(res):
                # 先删除目录下的file,最后删除文件夹
                del_filedir(res)
                os.rmdir(res)


def full_path(folder_path):
    # 使用os.walk遍历文件夹
    for root, directories, files in os.walk(folder_path):
        for file in files:
            # 拼接完整的文件路径
            full_path = os.path.join(root, file)
            # 打印文件路径
            return full_path
    return None
