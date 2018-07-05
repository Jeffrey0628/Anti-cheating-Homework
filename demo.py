#/usr/bin/env python
#!coding:utf-8  
import os
import hashlib
import re
import sys
import Queue

def find_pair(id_path_dict, id_name_dict, source="1603121431尹振飞.zip"):
    decode_message = source
    #匹配学号
    number = r'\d+'
    number_pattern = re.compile(number)
    number_result = number_pattern.match(decode_message)
    no = 0
    if number_result:
        no = number_result.group()
    # 添加id_path字典
    id_path_pair = {}
    current_path = os.path.abspath(source)
    id_path_pair[no] = current_path
    # print(no)
    #匹配姓名
    decode_message = source.decode('utf8')
    name = u"([\u4e00-\u9fff]+)"
    pattern = re.compile(name)
    results = pattern.findall(decode_message)
    id_name_pair = {}
    if results:
        id_name_pair[no] = results[0]

    id_name_dict.update(id_name_pair)
    id_path_dict.update(id_path_pair)
     

     
def get_file_md5(f):
    m = hashlib.md5()

    while True:
        data = f.read(10240)
        if not data:
            break
        m.update(data)
    return m.hexdigest()


# def traverse_all_file(path='.'):
#     files = os.listdir(path)
#     results = []
#     for file in files:
#         if not os.path.isdir(file):
#         #    print(file)
#             pair = find_pair(file)
#             with open(file, 'rb') as f:
#                 md5 =get_file_md5(f)
#                 # print(md5)
#                 if pair: 
#                     pair.append(md5)
#                     results.append(pair)
#     return results

def collect_homework(homework_dict = {}, id_name_dict = {}, id_path_dict = {}, root_path="."):
    name_dir = os.listdir(root_path)
    for file in name_dir:
        if os.path.isdir(file):
            find_pair(id_path_dict, id_name_dict, file)

    dict1_keys = id_path_dict.keys()
    print(len(dict1_keys))
    for id in dict1_keys:
        # print(id)
        # print(id_path_dict[id])
        stu_path = id_path_dict[id]    # 对应文件夹根目录，取到的是绝对路径
        # print(stu_path)
        
        rest_dir = Queue.Queue()
        rest_dir.put(stu_path)
        # 暂存某个id对应得到全部path:md5对应关系
        file_list = []
        while not rest_dir.empty():
            # 从队列顶端拿取待处理的文件/文件夹，是绝对路径
            tmp_path = rest_dir.get()
            # 如果是目录则加入队列
            if os.path.isdir(tmp_path): 
                files = os.listdir(tmp_path)
                for file in files:
                    rest_dir.put(tmp_path+'/'+file)
            # 如果是文件则处理，将{绝对路径：md5}放入list中
            else:
                # print(tmp_path)
                with open(tmp_path, "r") as file:
                # with open(tmp_path, "r") as file:
                    file_md5 = get_file_md5(file)   
                file_path = os.path.abspath(tmp_path)
                file_list.append({file_path:file_md5})
        # 将学号：文件list存入homework_dict中
        homework_dict.update({id:file_list})



    # rest_path = Queue.Queue()
    # rest_path.put(root_path)
    # while not rest_path.empty():
    #     tmp_path = rest_path.get()
    #     if os.path.isdir(tmp_path):
    #         files = os.listdir(temp_path)
    #         for file in files:
    #             rest_path.put(file)
    #     else: #if tmp_path is file

            
    #     files = os.listdir(path)
    #     for file in files:
    #         rest_path.put(file)

    # files = os.listdir(path)
    # for file in files:
    #     if 

if __name__ == "__main__" :

    #创建要写入的log文件
    log = "./log1.txt"
    log_file = open(log, "w")
    md5_log = "./file_all1.txt"
    md5_file = open(md5_log, "w")

    # 测试正则表达式  
    reload(sys)  
    sys.setdefaultencoding("utf-8")


    # 初始化参数
    path = "."
    homework_dict = {}
    id_name_dict = {}   
    id_path_dict = {}
    collect_homework(homework_dict, id_name_dict, id_path_dict, path)

    ids = id_name_dict.keys()
    for id in ids:
        # print(id),
        # print(id_name_dict[id])
        log_file.write(id + " " + id_name_dict[id] + "\r\n")
        

    # 构造结果集
    # results [{id1:{1:{}, 2:{}, 3{}}}]
    results = []

    # 所有文件的合集
    md5_all = set()

    # homework_dict
    # {
    #   id1:[
    #           {file1 : md5_1}, 
    #           {file2 : md5_2}, 
    #           {file3 : md5_3}
    #       ], 
    #   id2:[
    #           {file1 : md5_1}, 
    #           {file2 : md5_2}, 
    #           {file3 : md5_3}
    #       ],
    #   ...
    # }
    ids = homework_dict.keys()
    for id in ids:
        md5_tmp = set()
        log_file.write(id+" : ")
        for lst_file_pair in homework_dict[id]:

            file_path = lst_file_pair.keys()
            for k in file_path:
                # print(k),
                # print(lst_file_pair[k])
                if lst_file_pair[k] in md5_all:
                    print(id + " "+ k + " " + lst_file_pair[k])
                elif lst_file_pair[k] in md5_tmp:
                    pass
                else:
                    md5_tmp.add(lst_file_pair[k])
                log_file.write("\r\n    ")
                log_file.write(k+" "+lst_file_pair[k])
        log_file.write("\r\n")
        print("\r\nabc\r\n"+len(md5_tmp))
        md5_all.update(md5_tmp)
    
    for e in md5_all:
        md5_file.write(e+"\r\n")

    log_file.close()
    md5_file.close()

    




