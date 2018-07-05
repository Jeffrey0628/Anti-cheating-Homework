#/usr/bin/env python
#!coding:utf-8  

##########################################################################
# python2.7
# 这是一个简单的查重脚本
# 文档结构必须如下
# ├── path
# │   ├── 1603121431尹振飞
# │   │   ├── file1
# │   │   ├── file2
# │   │   └── dir1
# │   │       └── file3
# │   ├── 1600312433裸羊
# │   │   ├── file1
# |   |   └── dir1
# │   │       └── file2
# 1. 根目录path
# 2. 根目录下单每一个文件夹以"学号姓名"命名，作为每个学生的目录
# 3. 文件夹层数无要求，文件名无要求
# 输出结果在 results_log_path
##########################################################################

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


# homework_dict
# {
#   id1:[                     ----homework_dict[id]
#           {file1 : md5_1},  ----lst_file_pair
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

# 将结果的详细信息写入results_log中，格式为按照文件名作为key，各项为相同的其他文件
def find_cheater(homework_dict, results_log_path):
    ids = homework_dict.keys()
    # results结构
    # {
    #   id1:{                                       
    #           file1 :                             ----record结构为file:[file1, file2]
    #                   [ file2, file3, file4 ],    ----item
    #           file2 : 
    #                   [ file2, file3, file4 ], 
    #           file3 : 
    #                   [ file2, file3, file4 ]
    #       {, 
    #   id2:{
    #           file1 : [ file2, file3, file4 ], 
    #           file2 : [ file2, file3, file4 ], 
    #           file3 : [ file2, file3, file4 ]
    #       },
    #   ...
    # }
    results = {}
    for id in ids:
        record = {}
        for lst_file_pair in homework_dict[id]:
            
            file_path = lst_file_pair.keys()
            # 得到某个pair重复的全部文件list，存放于item中
            # k是具体的文件目录
            for k in file_path:
                item = []

                to_compare_md5 = lst_file_pair[k]

                # 遍历找相同
                for compared_id in ids:
                    if compared_id != id:
                        for compared_pair in homework_dict[compared_id]:
                            compared_file = compared_pair.keys()
                            for file_path in compared_file:
                                compared_md5 = compared_pair[file_path]
                                if to_compare_md5 == compared_md5:
                                    item.append(file_path)
                if item:
                    record[k] = item
        if record:
            results[id] = record
    
    ids = results.keys()
    for id in ids:
        records = results[id]
        records_keys = records.keys()
        print("id:"+id+"")
        for source_file in records_keys:
            cheated_list = records[source_file]
            print("  source file:")
            print("    "+source_file)
            print("  cheated file:")
            for file in cheated_list:
                print("    " + file)
            


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
        # 存放对应ID的md5集
        md5_tmp = set()
        log_file.write(id+" : ")
        for lst_file_pair in homework_dict[id]:

            file_path = lst_file_pair.keys()
            for k in file_path:
                # print(k),
                # print(lst_file_pair[k])
                if lst_file_pair[k] in md5_all:
                    # !!!!! 这个地方可以显示结果
                    # print(id + " "+ k + " " + lst_file_pair[k])
                    pass
                elif lst_file_pair[k] in md5_tmp:
                    pass
                else:
                    md5_tmp.add(lst_file_pair[k])
                log_file.write("\r\n    ")
                log_file.write(k+" "+lst_file_pair[k])
        log_file.write("\r\n")
        md5_all.update(md5_tmp)
    
    for e in md5_all:
        md5_file.write(e+"\r\n")

    # 将抄袭的详细信息写入log
    results_log_path = "./results.log"
    find_cheater(homework_dict, results_log_path)



    log_file.close()
    md5_file.close()

    




