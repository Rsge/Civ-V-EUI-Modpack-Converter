#######################################################
#                                                     #
# © 2022 - MPL 2.0 - Rsge - v2.0.0                    #
# https://github.com/Rsge/Civ-V-EUI-Modpack-Converter #
#                                                     #
# WINDOWS ONLY!                                       #
#                                                     #
#######################################################

# TODO Auto-detection of unit UI changing elements in mods possible?

# Imports
import os
import winreg as wr
from os.path import join as j
from glob import glob as g
import subprocess
import shutil
import re

## Global Values
print("Configuring variables...")

# Names
modpack_folder_name = "MP_MODSPACK"
eui_cuc_file_names = ["CityBannerManager.lua",
                      "CityView.lua",
                      "Highlights.xml"]
load_tag = "ContextPtr:LoadNewContext"
unit_panel_file_name = "UnitPanel.lua"
ige_compat_file_name = "IGE_Window.lua"

###########################################
# Customize these according to your setup #
###########################################
vanilla_eui_zip = "!EUI.7z" # Vanilla EUI file (in vanilla_packs_folder)
modded_eui_zip = "!EUI_CUC.7z" # CUC-version file name of EUI
vanilla_packs_folder = "zz_Vanilla_Versions" # Folder containing the vanilla packs in DLC folder
unit_panel_modcompat_file_names = ["EvilSpiritsMission.lua", # Mod files adding new actions to units
                                   "THTanukiMission.lua"]

###################################################################################################
# Don't change after here [except if you know what you're doing of cause ;)]                      #
#                                                                                                 #
# YOU'LL NEED 7-ZIP!                                                                              #
# If you want to use WinRar you'll have to change the methods yourself - or just download 7zip =P #
###################################################################################################

# Closing functions
null = open(os.devnull, 'w')
def quit():
    null.close()
    print("Done.\n")
    input("Press Enter to exit. . .")
    exit(0)
def error(msg):
    null.close()
    print("Error!\n{}\n".format(msg))
    input("Press Enter to exit. . .")
    exit(1)

# Get file name
def get_file_name(file, get_folder = False):
    return file.split(os.sep)[-1]

# Get 7-zip install dir
def get_szip_dir():
    key_location = r"SOFTWARE\7-Zip"
    value = "Path"
    try:
        key = wr.OpenKey(wr.HKEY_LOCAL_MACHINE, key_location)
        install_dir = wr.QueryValueEx(key, value)[0]
        wr.CloseKey(key)
    except:
        error("No 7-zip installation found!\nIf you insist on using WinRar, change the script yourself ¯\_(ツ)_/¯")
    return install_dir

# Get Civ V install dir
def get_civ_install_dir():
    key_location = r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\steam app 8930"
    value = "installlocation"
    try:
        key = wr.OpenKey(wr.HKEY_LOCAL_MACHINE, key_location)
        install_dir = wr.QueryValueEx(key, value)[0]
        wr.CloseKey(key)
    except:
        error("No Civ 5 installation found!")
    return install_dir

# Paths
szip = j(get_szip_dir(), "7z.exe")
modsave_path = j(os.getcwd(), "..")
base_path = j(get_civ_install_dir(), "Assets", "DLC")
vanilla_packs_path =  j(base_path, vanilla_packs_folder)
eui_folder_path = j(base_path, "UI_bc1")
modpack_path = j(base_path, modpack_folder_name)
ui_folder_path = j(modpack_path, "UI")
# Files
files_ext = j("**", "*.lua")
base_ui_files = j(base_path, "..", "UI", files_ext)
gnk_ui_files = j(base_path, "Expansion", "UI", files_ext)
bnw_ui_files = j(base_path, "Expansion2", "UI", files_ext)
vanilla_eui_zip_path = j(vanilla_packs_path, vanilla_eui_zip)
modded_eui_zip_path = j(base_path, modded_eui_zip)
mod_files = j(modpack_path, "Mods", files_ext)
ui_files = j(ui_folder_path, files_ext)
eui_files = j(eui_folder_path, files_ext)

# Global Variables
eui_only = False
vanilla_ui_files = []
load_tags = {}
unit_panel_modcompat_needed = False


# Change working dir to base path
os.chdir(base_path)

# Get modpack zip
while True:
    modpack_name = input("\nWhich pack should be converted?\n(Type 'EUI' to just convert EUI)\n")
    if modpack_name == "EUI":
        eui_only = True
        break
    modpack_zips = g(j(vanilla_packs_path, modpack_name + ".*"))
    if len(modpack_zips) > 0:
        modpack_zip = modpack_zips[0]
        break
    print("This file doesn't exist, try again.")


# Remove previous modpack
print("\nRemoving previous modpack and EUI leftovers...")
if os.path.isdir(modpack_path):
    shutil.rmtree(modpack_path)
if os.path.isdir(eui_folder_path):
    shutil.rmtree(eui_folder_path)

# Compile EUI with colored unlocked citizens
if not os.path.isfile(modded_eui_zip_path):
    print("Creating colored unlocked citizens EUI...")
    subprocess.run([szip, 'x', vanilla_eui_zip_path], stdout=null, stderr=null)
    for eui_cuc_file_name in eui_cuc_file_names:
        eui_cuc_file = g(j(modsave_path, eui_cuc_file_name + "*"))[0]
        orig_eui_file = g(j(eui_folder_path, "*", eui_cuc_file_name))[0]
        shutil.move(orig_eui_file, orig_eui_file + ".orig")
        shutil.copyfile(eui_cuc_file, orig_eui_file)
    subprocess.run([szip, 'a', modded_eui_zip, eui_folder_path], stdout=null, stderr=null)
else:
    # Unzip EUI
    print("Unzipping EUI...")
    subprocess.run([szip, 'x', modded_eui_zip_path], stdout=null, stderr=null)

# Stop here if only EUI should be converted
if eui_only:
    quit()


# Unzip modpack zip
print("Unzipping Modpack...")
subprocess.run([szip, 'x', j(vanilla_packs_path, modpack_zip)], stdout=null, stderr=null)


# Get vanilla UI files
print("Gathering Vanilla UI file list...")
globbed = g(base_ui_files, recursive=True)
globbed.extend(g(gnk_ui_files, recursive=True))
globbed.extend(g(bnw_ui_files, recursive=True))
for file in globbed:
    file_name = get_file_name(file)
    if not file_name in ui_files:
        vanilla_ui_files.append(file_name)

# Manage mod files
for mod_file in g(mod_files, recursive = True):
    mod_file_name = get_file_name(mod_file)
    mod_file_folder = os.sep.join(mod_file.split(os.sep)[-3:-1])

    # IGE UI compat file
    if mod_file_name == ige_compat_file_name:
        print("Providing IGE-EUI-compat...")
        shutil.move(mod_file, mod_file + ".orig")
        shutil.copyfile(g(j(modsave_path, ige_compat_file_name + "*"))[0], mod_file)

    # Delete UI overwrite duplicates
    if mod_file_name in vanilla_ui_files:
        print("Removing overwriting file {}...".format(j(mod_file_folder, mod_file_name)))
        os.remove(mod_file)

    # Find out if modcompat unit panel needed
    if mod_file_name in unit_panel_modcompat_file_names:
        print("UnitPanel modcompat need detected...")
        unit_panel_modcompat_needed = True

# Delete useless desktop.ini (Thanks True...)
ini_files = re.sub(r"\.\w+$", ".ini", mod_files)
for ini_file in g(ini_files, recursive = True):
    ini_file_name = get_file_name(ini_file)
    if ini_file_name == "desktop.ini":
        print("Removing useless desktop.ini (Thanks True)...")
        os.remove(mod_file)


# Get stuff from UI files
for ui_file in g(ui_files):        
    ui_file_name = get_file_name(ui_file)
    print("Getting tags from " + ui_file_name + "...")

    load_tags[ui_file_name] = []
    
    with open(ui_file, 'r') as file:
        lines = file.readlines()

    for line in lines:
        if line.startswith(load_tag):
            load_tags[ui_file_name].append(line)

# Insert stuff into EUI files
for eui_file in g(eui_files):
    eui_file_name = get_file_name(eui_file)

    # Base UI files
    if eui_file_name in load_tags.keys():
        print("Writing tags to " + eui_file_name + "...")
        with open(eui_file, 'a') as file:
            file.write('\n')
            for load_tag in load_tags[eui_file_name]:
                file.write(load_tag)
    # Modcompat unit panel
    elif eui_file_name == unit_panel_file_name and unit_panel_modcompat_needed:
        print("Providing EUI-UnitPanel-Modcompat...")
        shutil.move(eui_file, eui_file + ".orig")
        shutil.copyfile(g(j(modsave_path, unit_panel_file_name + "*"))[0], eui_file)


# Move EUI folder
print("Moving EUI folder...")
shutil.move(eui_folder_path, modpack_path)
print("Removing UI folder...")
shutil.rmtree(ui_folder_path)

# Zip modpack folder
print("Zipping Modpack...")
subprocess.run([szip, 'a', modpack_name + "_EUI.7z", modpack_path], stdout=null, stderr=null)

#Finishing up
quit()