"""
Title: main.py
By: M5DS1
    Purpose: execute dataparser script on every json file in the specified directory

"""

import os
from data_parser import *



''' Only Change This!! '''
# json_dir = 'Decrypted/Intel/'
# json_dir = 'Decrypted/Viper/'
# json_dir = 'Decrypted/Solo/solo_decrypted_json_20200217/'
json_dir = 'Decrypted/Solo/solo_decrypted_json_20200223/'
results_dir = 'Results/'
includes_dir = 'Includes/v1.0/'

for json_file in os.listdir(json_dir):
    if json_file.endswith(".json"):
        data_parser(json_dir, os.path.splitext(json_file)[0], results_dir, includes_dir)


