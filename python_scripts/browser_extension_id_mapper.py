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
import urllib.request
from datetime import datetime
import os
import re
import json


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
            return response.read().decode('utf-8')
    except Exception as e:
        return ""


def map_list_of_ext_ids(list_of_ext_ids: list, browser: str) -> dict:
    ret_dict = {}
    if browser == 'chrome':
        for ext_id in list_of_ext_ids:
            ret_dict[ext_id] = map_chrome_ext_id(ext_id)
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


def local_run(outfile: str):
    # starting with the logic for chrome extension ID mapping. NOTE: a simple urllib request can be used for these
    # dict for mapping local users to their extensions
    user_chrome_ext_dict = {}
    outfile = outfile
    list_of_users = get_users_folderpaths()
    for user in list_of_users:
        ext_names = get_exts_from_folderpath(skeleton_path_to_chrome_extensions.format(user=user))
        user_chrome_ext_dict[user] = ext_names

    # logic for getting the names/descriptions from the chrome store
    for user, chrome_ext_list in user_chrome_ext_dict.items():
        if chrome_ext_list is not None:
            user_chrome_ext_dict[user] = map_list_of_ext_ids(chrome_ext_list, 'chrome')

    # for testing purposes
    json_output = json.dumps(user_chrome_ext_dict, indent=2)
    print(f"JSON version of output:\n{json_output}")



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
    parser.add_argument('-o', '--outfile', help='arg to tell script where to print CSV output, default is .\\<dateTime>_originalFilename_mapped.csv.')
    parser.add_argument('-l', '--local',
                        help='arg to run the script against local machine and users. default is false', default=False, choices=['true', 'false'])
    parser.add_argument('-f', '--filename', help='arg for the file with the Browser Extension IDs. looking for a flat txt file.')

    args = parser.parse_args()

    #mapping cmdline args to vars for future use
    local_run_bool = args.local
    ext_file = args.filename
    outfile = args.outfile
    if not outfile:
        dt = get_datetime()
        outfile = f"{dt}_{ext_file}_mapped.csv"
    print(f"[*] output will be placed in {outfile}")

    #logic for a local mapping, looking in all users for C:\users\<username>\AppData\Local\Google\Chrome\User Data\Default\Extensions
    if local_run_bool:
        local_run(outfile)

if __name__ == "__main__":
    main()

