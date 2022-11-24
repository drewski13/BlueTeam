#
#
#
#
#
#
# by Drewski1313
###########################################

#imports
import argparse
import html
import urllib.request
from datetime import datetime
import os
import re
import json
import csv
from selenium import webdriver


#GLOBALS
art = '''
oooooooooooo                 .      ooooo oooooooooo.      ooo        ooooo
`888'     `8               .o8      `888' `888'   `Y8b     `88.       .888'
 888         oooo    ooo .o888oo     888   888      888     888b     d'888   .oooo.   oo.ooooo.  oo.ooooo.   .ooooo.  oooo d8b
 888oooo8     `88b..8P'    888       888   888      888     8 Y88. .P  888  `P  )88b   888' `88b  888' `88b d88' `88b `888""8P
 888    "       Y888'      888       888   888      888     8  `888'   888   .oP"888   888   888  888   888 888ooo888  888
 888       o  .o8"'88b     888 .     888   888     d88'     8    Y     888  d8(  888   888   888  888   888 888    .o  888
o888ooooood8 o88'   888o   "888"    o888o o888bood8P'      o8o        o888o `Y888""8o  888bod8P'  888bod8P' `Y8bod8P' d888b
                                                                                       888        888
                                                                                      o888o      o888o
'''
skeleton_path_to_chrome_extensions = "C:\\Users\\{user}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Extensions"
skeleton_path_to_edge_extensions = "C:\\Users\\{user}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Extensions"
chrome_baseURL = 'https://chrome.google.com/webstore/detail/'
edge_baseURL = 'https://microsoftedge.microsoft.com/addons/detail/'


#FUNCTIONS
def get_datetime() -> str:
    now = datetime.now()
    dt_string = now.strftime("%d%b%Y_%H.%M")
    return dt_string


def get_users_folderpaths() -> list:
    subfolders = [f.path for f in os.scandir("C:\\users") if f.is_dir()]
    only_users_foldernames = [get_last_foldername(folder) for folder in subfolders]
    return only_users_foldernames


def get_exts_from_folderpath(ext_folder: str) -> list:
    if not os.path.exists(ext_folder):
        return
    subfolders = [f.path for f in os.scandir(ext_folder) if f.is_dir()]
    only_ext_names = [get_last_foldername(folder) for folder in subfolders if '\\Temp' not in folder]
    return only_ext_names


def get_last_foldername(full_path: str) -> str:
    return re.sub(".*\\\\", "", full_path)


# helper function to return a string of the webpage returned by the method to the URL
#relies on IMPORTing urllib.request
def get_to_url(url: str, method: str) -> str:
    try:
        req = urllib.request.Request(url, method=method)
        with urllib.request.urlopen(req) as response:
            return html.unescape(response.read().decode('utf-8'))
    except Exception as e:
        return ""


def map_list_of_ext_ids(list_of_ext_ids: list, browser: str) -> dict:
    ret_dict = {}
    if browser == 'chrome':
        for ext_id in list_of_ext_ids:
            ret_dict[ext_id] = map_chrome_ext_id(ext_id)
    elif browser == 'edge':
        for ext_id in list_of_ext_ids:
            ret_dict[ext_id] = map_edge_ext_id(ext_id)
    return ret_dict


def map_chrome_ext_id(ext_id: str) -> dict:
    full_webpage = get_to_url(f"{chrome_baseURL}{ext_id}", "GET")
    if not full_webpage:
        return {'name': "unknown", 'description': "no page reached for this ext ID"}
    else:
        ext_name_match = re.match(r'(?i).*\<title\>([^\<]+)\<\/title\>.*', full_webpage)
        if ext_name_match:
            ext_name = ext_name_match[1]
        else:
            ext_name = "no ext name found with regex"

        #slicing out data here just because it seems to give me more consistently correct results in testing
        desc_match = re.match(r'(?i).*description.?\>[^\<]+\<[^\>]+\>\<[^\>]+\>([^\<]*)\<\/.*', full_webpage[1000:])
        if ext_name_match:
            ext_desc = desc_match[1].replace("\n", "")
        else:
            ext_desc = "no ext description found with regex"
    return {'name': ext_name, 'description': ext_desc}


def write_ext_dict_to_csv_file(csv_file: str, ext_dict: dict, local_run: str, browser_type: str):
    if local_run == 'true':
        csv_columns = ['user', 'browser type', 'ext_id', 'name', 'description']
        csv_file = csv_file
        with open(csv_file, "a", newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for user, inner_ext_dict in ext_dict.items():
                if inner_ext_dict is not None:
                    for ext_id, nd in inner_ext_dict.items():
                        writer.writerow({'user': user, 'browser type': browser_type, 'ext_id': ext_id, 'name': nd['name'], 'description': nd['description']})
                else:
                    writer.writerow({'user': user, 'browser type': browser_type, 'ext_id': 'None', 'name': 'N/A',
                                     'description': 'N/A'})
    else:
        csv_columns = ['browser type', 'ext_id', 'name', 'description']
        csv_file = csv_file
        with open(csv_file, "a", newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for ext_id, nd in ext_dict.items():
                if nd is not None:
                    writer.writerow({'browser type': browser_type, 'ext_id': ext_id, 'name': nd['name'],'description': nd['description']})
                else:
                    writer.writerow({'browser type': browser_type, 'ext_id': 'None', 'name': 'N/A',
                                     'description': 'N/A'})


def map_edge_ext_id(ext_id: str) -> dict:
    dest_uri = edge_baseURL + ext_id
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("headless")
    chrome_options.add_argument('--log-level=3')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(dest_uri)
    headless_html = driver.page_source
    edge_addon_page = headless_html.replace("\n", "")
    # print(html)
    match = re.match(r'(?i).*Description\<.*\>([^\<]+)\<\/pre.*', edge_addon_page)
    if match:
        ext_desc = match[1].replace("\n", "")
        ext_desc = html.unescape(ext_desc)
    else:
        ext_desc = "no description match from regex of page"
    match2 = re.match(r'(?i).*\<title\>([^\<]+)\<\/title.*', edge_addon_page)
    if match2:
        ext_name = match2[1]
        ext_name = html.unescape(ext_name)
    else:
        ext_name = "no addon name match from regex of page"
    driver.quit()
    return {'name': ext_name, 'description': ext_desc}


def local_run(outfile: str):
    # starting with the logic for chrome extension ID mapping. NOTE: a simple urllib request can be used for these
    # dict for mapping local users to their extensions
    user_chrome_ext_dict = {}
    user_edge_ext_dict = {}
    # old way: outfile = outfile, new logic for 2 files
    chrome_outfile = outfile.replace("browser-type", "chrome")
    edge_outfile = outfile.replace("browser-type", "edge")
    list_of_users = get_users_folderpaths()
    for user in list_of_users:
        ext_names = get_exts_from_folderpath(skeleton_path_to_chrome_extensions.format(user=user))
        user_chrome_ext_dict[user] = ext_names
        ext_names = get_exts_from_folderpath(skeleton_path_to_edge_extensions.format(user=user))
        user_edge_ext_dict[user] = ext_names

    # logic for getting the names/descriptions from the chrome store
    for user, chrome_ext_list in user_chrome_ext_dict.items():
        if chrome_ext_list is not None:
            user_chrome_ext_dict[user] = map_list_of_ext_ids(chrome_ext_list, 'chrome')

    # logic for getting the names/descriptions from the edge store
    for user, edge_ext_list in user_edge_ext_dict.items():
        if edge_ext_list is not None:
            user_edge_ext_dict[user] = map_list_of_ext_ids(edge_ext_list, 'edge')

    # for testing purposes
    chrome_json_output = json.dumps(user_chrome_ext_dict, indent=2)
    edge_json_output = json.dumps(user_edge_ext_dict, indent=2)
    print(f"JSON version of output:\nChrome Extensions:\n{chrome_json_output}\nEdge Addons:\n{edge_json_output}")

    #writing output CSV file
    write_ext_dict_to_csv_file(chrome_outfile, user_chrome_ext_dict, 'true', 'chrome')
    write_ext_dict_to_csv_file(edge_outfile, user_edge_ext_dict, 'true', 'edge')


def input_file_run(ext_file: str, outfile: str, browsertype: str):
    file_to_process = ext_file
    ext_list = ret_list_from_txt_file(file_to_process)
    browser_type = browsertype
    ext_outfile = outfile.replace("browser-type", browser_type)
    if browser_type == 'chrome':
        mapped_ext_dict = map_list_of_ext_ids(ext_list, 'chrome')
    elif browser_type == 'edge':
        mapped_ext_dict = map_list_of_ext_ids(ext_list, 'edge')

    write_ext_dict_to_csv_file(ext_outfile, mapped_ext_dict, 'false', browser_type)


def ret_list_from_txt_file(filename: str) -> list:
    ret_list_final = []
    with open(filename, "r") as f:
        ret_list = f.read().split("\n")
    for item in ret_list:
        if len(item) > 20:
            ret_list_final.append(item)
    return ret_list_final

#MAIN
def main():
    #printing ascii art is fun
    print(art)
    #use of argparse for commandline arguments and script information
    parser = argparse.ArgumentParser(
        description='This script will take a list of browser IDs, unique them and return their names and descriptions from the appropriate online store.',
        )
    # list of required args for clarity in help output
    #requiredNamed = parser.add_argument_group('required arguments')
    #requiredNamed.add_argument('-f', '--filename', help='arg for the file with the Browser Extension IDs. looking for a flat txt file.')

    #list of optional args
    parser.add_argument('-o', '--outpath', help='arg to tell script a path to print CSV output. default is .\\<dateTime>_originalFilename_mapped.csv.')
    parser.add_argument('-l', '--local',
                        help='arg to run the script against local machine and users. default is false', default=False, choices=['true', 'false'])
    parser.add_argument('-f', '--filename', help='arg for the file with the Browser Extension IDs. looking for a flat txt file.')
    parser.add_argument('-b', '--browsertype',
                        help='arg for use with -f flag to tell script browser type of provided extension IDs', choices=['chrome', 'edge'])

    args = parser.parse_args()

    #mapping cmdline args to vars for future use
    local_run_bool = args.local
    browser_type = args.browsertype
    ext_file = args.filename
    if ext_file is None:
        ext_file = 'local'
    outpath = args.outpath
    dt = get_datetime()
    if not outpath:
        outfile = f"{dt}_{ext_file}_browser-type_mapped.csv"
    else:
        if outpath[-1] == "\\":
            outfile = f"{outpath}{dt}_{ext_file}_browser-type_mapped.csv"
        else:
            outfile = f"{outpath}\\{dt}_{ext_file}_browser-type_mapped.csv"

    print(f"[*] output will be placed in {outfile}")

    #local run or else passed a file with extension IDs
    if local_run_bool:
        local_run(outfile)
    else:
        input_file_run(ext_file, outfile, browser_type)


if __name__ == "__main__":
    main()

