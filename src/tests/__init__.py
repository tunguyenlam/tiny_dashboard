import os
from os import listdir
from os.path import join, isfile
from src.configuration import settings

github_data_folder = settings.BASE_DIR + "/data/github/"

dfs_dict = {}
# for file_name in os.walk(github_data_folder):
#     if os.path.isfile(file_name):
#         print(file_name)

dfs_dict = {}
for f in listdir(github_data_folder):
    file_path = join(github_data_folder, f)
    if isfile(file_path) and '.csv' in f:
        dfs_dict[f.replace('.csv', '')] = file_path

print(dfs_dict)