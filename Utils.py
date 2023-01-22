import os
import shutil
import re as regex


def regex_main(content, userid, fp):
    reg = "/" + fp + "/user/" + str(userid) + "/post/[0-9]+"
    result = regex.findall(reg, content)
    return list(set(result))


def regex_sub(content, regex_):
    result = regex.findall(regex_, content)
    return list(set(result))


def delete_tmp_files():
    dir_name = os.getcwd()
    test = os.listdir(dir_name)
    for item in test:
        if item.endswith(".tmp"):
            os.remove(os.path.join(dir_name, item))


def update_iteration(iteration, iter_file_name):
    iteration_file = open(iter_file_name, "w")
    iteration_file.write(str(int(iteration) + 1))
    iteration_file.close()


def create_iteration(iter_file_name):
    if not os.path.exists(iter_file_name):
        open(iter_file_name, 'w').write("0")


def move_links(folder, iteration):
    links_dir = "Links"
    other_dir = "Misc"
    links_path = os.path.join(folder, links_dir)
    if not os.path.exists(links_path):
        os.mkdir(links_path)
    other_path = os.path.join(folder, other_dir)
    if not os.path.exists(other_path):
        os.mkdir(other_path)
    shutil.move(str(os.getcwd() + "/" + "RedLinks_" + iteration + ".txt"), links_path)
    shutil.move(str(os.getcwd() + "/" + "Links_" + iteration + ".txt"), links_path)
    shutil.move(str(os.getcwd() + "/" + "Problematic_links_" + iteration + ".txt"), links_path)
    shutil.move(str(os.getcwd() + "/" + "Data_" + iteration + ".txt"), other_path)


class Utils:
    pass
