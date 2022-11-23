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
from datetime import datetime
import os
import re


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


#FUNCTIONS
def get_datetime():
    now = datetime.now()
    dt_string = now.strftime("%d%b%Y_%H.%M")
    return dt_string


def get_users_folderpaths():
    subfolders = [f.path for f in os.scandir("C:\\users") if f.is_dir()]
    only_users_foldernames = [get_last_foldername(folder) for folder in subfolders]
    return only_users_foldernames


def get_exts_from_folderpath(ext_folder):
    if not os.path.exists(ext_folder):
        return
    subfolders = [f.path for f in os.scandir(ext_folder) if f.is_dir()]
    only_ext_names = [get_last_foldername(folder) for folder in subfolders if '\\Temp' not in folder]
    return only_ext_names


def get_last_foldername(full_path):
    return re.sub(".*\\\\", "", full_path)


def local_run(outfile):
    #dict for mapping local users to their extensions
    user_ext_dict = {}
    outfile = outfile
    list_of_users = get_users_folderpaths()
    for user in list_of_users:
        ext_names = get_exts_from_folderpath(skeleton_path_to_chrome_extensions.format(user=user))
    print(ext_names)


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
    print(f"output will be placed in {outfile}")

    #logic for a local mapping, looking in all users for C:\users\<username>\AppData\Local\Google\Chrome\User Data\Default\Extensions
    if local_run_bool:
        local_run(outfile)

if __name__ == "__main__":
    main()

