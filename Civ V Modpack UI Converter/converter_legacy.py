########################################################################
#                                                                      #
# © 2021 - MPL 2.0 - Rsge - v1.0.4                                     #
# https://github.com/Rsge/Civ-V-EUI-Modpack-Converter                  #
#                                                                      #
# WINDOWS ONLY!                                                        #
# 7-ZIP NEEDED!                                                        #
# If you want to use WinRar you'll have to change the methods yourself #
# (or just download 7-zip =P)                                          #
#                                                                      #
########################################################################


#------------------------------------------#
# Customize these according to your setup: #
#------------------------------------------#

# Vanilla EUI file (in vanilla_packs_folder)
VANILLA_EUI_ZIP = "!EUI.7z"

# CUC-version file name of EUI
MODDED_EUI_ZIP = "!EUI_CUC.7z"

# Folder containing this scripts project folder and it's needed edited files
# (Sid Meier's Civilization V\Assets\DLC\ThisVariableAsFolderName)
MODSAVE_DIR = "zzz_Modsaves"

# Folder containing the vanilla packs
VANILLA_PACKS_DIR = "zz_Vanilla_Versions"

#--------------------------------------------#
# Maybe you also need to add to these lists: #
#--------------------------------------------#

# Mod files overwriting original UI files, conflicting with EUI
DELETE_FILE_NAMES = ["CivilopediaScreen.lua",
                     "CityView.lua",
                     "TechTree.lua",
                     "TechButtonInclude.lua"]

# Mod files adding new actions to units
UNIT_PANEL_MODPCOMPAT_FILE_NAME = ["EvilSpiritsMission.lua",
                                   "THTanukiMission.lua"]

#-----------------------------------------------------#
# Don't change anything after here!                   #
# [except if you know what you're doing of course ;)] #
#-----------------------------------------------------#

# Imports
import os
from os.path import join as j
from glob import glob as g
import subprocess
import shutil
import re

# Change to base DLC directory.
os.chdir("../..")

## Global values
print("Configuring variables...")
# Names
MODPACK_DIR_NAME = "MP_MODSPACK"
EUI_CUC_FILE_NAMES = ["CityBannerManager.lua",
                     "CityView.lua",
                     "Highlights.xml"]
LOAD_TAG = "ContextPtr:LoadNewContext"
UNIT_PANEL_FILE_NAME = "UnitPanel.lua"
IGE_COMPAT_FILE_NAME = "IGE_Window.lua"
# Paths
base_path = os.getcwd()
modsave_path = j(base_path, MODSAVE_DIR)
modpack_path = j(base_path, MODPACK_DIR_NAME)
vanilla_packs_path =  j(base_path, VANILLA_PACKS_DIR)
ui_path = j(modpack_path, "UI")
eui_path = j(base_path, "UI_bc1")
# Files
FILE_EXT = "*.lua"
base_eui_zip_path = j(vanilla_packs_path, VANILLA_EUI_ZIP)
modded_eui_zip_path = j(base_path, MODDED_EUI_ZIP)
mod_files = j(modpack_path, "Mods", "**", FILE_EXT)
ui_files = j(ui_path, FILE_EXT)
eui_files = j(eui_path, "*", FILE_EXT)
# This only runs with 7-zip. If you want to use WinRar you'll have to change the methods yourself - or just download 7-zip =P
SZIP = r"C:\Program Files\7-Zip\7z.exe"

# Global variables
load_tags = {}
unit_panel_modcompat_needed = False
null = open(os.devnull, 'w')
eui_only = False


# Quitting function
def quit():
    null.close()
    print("Done.\n")
    input("Press Enter to exit. . .")
    exit(0)

# Get modpack zip.
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


# Remove previous modpack.
print("Removing previous modpack leftovers...")
if os.path.isdir(modpack_path):
    shutil.rmtree(modpack_path)
if os.path.isdir(eui_path):
    shutil.rmtree(eui_path)

# Compile EUI with colored unlocked citizens.
if not os.path.isfile(modded_eui_zip_path):
    print("Creating colored unlocked Citizens EUI...")
    subprocess.run([SZIP, 'x', base_eui_zip_path], stdout=null, stderr=null)
    #shutil.move(j(vanilla_packs_path, eui_file_name), eui_path)
    for eui_cuc_file_name in EUI_CUC_FILE_NAMES:
        eui_cuc_file = g(j(modsave_path, eui_cuc_file_name + "*"))[0]
        orig_eui_file = g(j(eui_path, "*", eui_cuc_file_name))[0]
        shutil.move(orig_eui_file, orig_eui_file + ".orig")
        shutil.copyfile(eui_cuc_file, orig_eui_file)
    subprocess.run([SZIP, 'a', MODDED_EUI_ZIP, eui_path], stdout=null, stderr=null)
elif not eui_only:
    # Unzip EUI.
    print("Unzipping EUI...")
    subprocess.run([SZIP, 'x', modded_eui_zip_path], stdout=null, stderr=null)

# Stop here if only EUI should be converted.
if eui_only:
    if os.path.isdir(eui_path):
        shutil.rmtree(eui_path)
    quit()


# Unzip modpack zip.
print("Unzipping Modpack...")
subprocess.run([SZIP, 'x', j(vanilla_packs_path, modpack_zip)], stdout=null, stderr=null)


# Manage mod files.
for mod_file in g(mod_files, recursive = True):
    mod_file_path = mod_file.split(os.sep)
    mod_file_name = mod_file_path[len(mod_file_path) - 1]

    # IGE UI compat file
    if mod_file_name == IGE_COMPAT_FILE_NAME:
        print("Providing IGE-EUI-compat...")
        shutil.move(mod_file, mod_file + ".orig")
        shutil.copyfile(g(j(modsave_path, IGE_COMPAT_FILE_NAME + "*"))[0], mod_file)

    # Delete UI overwrite duplicates.
    if mod_file_name in DELETE_FILE_NAMES:
        print("Removing overwriting file " + mod_file_name + "...")
        os.remove(mod_file)

    # Find out if modcompat unit panel needed.
    if mod_file_name in UNIT_PANEL_MODPCOMPAT_FILE_NAME:
        print("UnitPanel modcompat need detected...")
        unit_panel_modcompat_needed = True

# Delete useless desktop.ini. (Thanks True...)
ini_files = re.sub(r"\.\w+$", ".ini", mod_files)
for ini_file in g(ini_files, recursive = True):
    ini_file_path = ini_file.split(os.sep)
    ini_file_name = ini_file_path[len(ini_file_path) - 1]
    if ini_file_name == "desktop.ini":
        print("Removing useless desktop.ini (Thanks True)...")
        os.remove(mod_file)


# Get stuff from UI files.
for ui_file in g(ui_files):
    with open(ui_file, 'r') as file:
        lines = file.readlines()
    ui_file_path = ui_file.split(os.sep)
    ui_file_name = ui_file_path[len(ui_file_path) - 1]
    print("Getting tags from " + ui_file_name + "...")
    load_tags[ui_file_name] = []
    for line in lines:
        if line.startswith(LOAD_TAG):
            load_tags[ui_file_name].append(line)

# Insert stuff into EUI files.
for eui_file in g(eui_files):
    eui_file_path = eui_file.split(os.sep)
    eui_file_name = eui_file_path[len(eui_file_path) - 1]
    # Base UI files
    if eui_file_name in load_tags.keys():
        print("Writing tags to " + eui_file_name + "...")
        with open(eui_file, 'a') as file:
            file.write('\n')
            for LOAD_TAG in load_tags[eui_file_name]:
                file.write(LOAD_TAG)
    # Modcompat unit panel
    elif eui_file_name == UNIT_PANEL_FILE_NAME and unit_panel_modcompat_needed:
        print("Providing EUI-UnitPanel-Modcompat...")
        shutil.move(eui_file, eui_file + ".orig")
        shutil.copyfile(g(j(modsave_path, UNIT_PANEL_FILE_NAME + "*"))[0], eui_file)


# Move EUI folder.
print("Moving EUI folder...")
shutil.move(eui_path, modpack_path)
print("Removing UI folder...")
shutil.rmtree(ui_path)

# Zip modpack folder.
print("Zipping Modpack...")
subprocess.run([SZIP, 'a', modpack_name + "_EUI.7z", modpack_path], stdout=null, stderr=null)

# Finish up.
quit()