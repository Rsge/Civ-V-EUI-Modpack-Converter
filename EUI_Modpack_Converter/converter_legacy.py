########################################################################
#                                                                      #
# © 2021 - MPL 2.0 - Rsge - v1.0.1                                     #
# https://github.com/Rsge/Civ-V-EUI-Modpack-Converter                  #
#                                                                      #
# WINDOWS ONLY!                                                        #
# 7-ZIP NEEDED!                                                        #
# If you want to use WinRar you'll have to change the methods yourself #
# (or just download 7-zip =P)                                          #
#                                                                      #
########################################################################


#-----------------------------------------#
# Customize these according to your setup #
#-----------------------------------------#

# Vanilla EUI file (in vanilla_packs_folder)
vanilla_eui_zip = "!EUI.7z"

# CUC-version file name of EUI
modded_eui_zip = "!EUI_CUC.7z"

# Folder containing this scripts project folder and it's needed edited files
modsave_folder = "zzz_Modsaves"

# Folder containing the vanilla packs
vanilla_packs_folder = "zz_Vanilla_Versions"

#-------------------------------------------#
# Maybe you also need to add to these lists #
#-------------------------------------------#

# Mod files overwriting original UI files, conflicting with EUI
delete_file_names = ["CivilopediaScreen.lua",
                     "CityView.lua",
                     "TechTree.lua",
                     "TechButtonInclude.lua"]

# Mod files adding new actions to units
unit_panel_modcompat_file_names = ["EvilSpiritsMission.lua",
                                   "THTanukiMission.lua"]

#----------------------------------------------------#
# Don't change anything after here                   #
# [except if you know what you're doing of cause ;)] #
#----------------------------------------------------#

# Imports
import os
from os.path import join as j
from glob import glob as g
import subprocess
import shutil
import re

# Change to base DLC directory
os.chdir("../..")

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
# Paths
base_path = os.getcwd()
modsave_path = j(base_path, modsave_folder)
modpack_path = j(base_path, modpack_folder_name)
vanilla_packs_path =  j(base_path, vanilla_packs_folder)
ui_path = j(modpack_path, "UI")
eui_path = j(base_path, "UI_bc1")
# Files
file_ext = "*.lua"
base_eui_zip_path = j(vanilla_packs_path, vanilla_eui_zip)
modded_eui_zip_path = j(base_path, modded_eui_zip)
mod_files = j(modpack_path, "Mods", "**", file_ext)
ui_files = j(ui_path, file_ext)
eui_files = j(eui_path, "*", file_ext)
# This only runs with 7zip. If you want to use WinRar you'll have to change the methods yourself - or just download 7zip =P
szip = r"C:\Program Files\7-Zip\7z.exe"

# Global Variables
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
print("Removing previous modpack leftovers...")
if os.path.isdir(modpack_path):
    shutil.rmtree(modpack_path)
if os.path.isdir(eui_path):
    shutil.rmtree(eui_path)

# Compile EUI with colored unlocked citizens
if not os.path.isfile(modded_eui_zip_path):
    print("Creating colored unlocked Citizens EUI...")
    subprocess.run([szip, 'x', base_eui_zip_path], stdout=null, stderr=null)
    #shutil.move(j(vanilla_packs_path, eui_file_name), eui_path)
    for eui_cuc_file_name in eui_cuc_file_names:
        eui_cuc_file = g(j(modsave_path, eui_cuc_file_name + "*"))[0]
        orig_eui_file = g(j(eui_path, "*", eui_cuc_file_name))[0]
        shutil.move(orig_eui_file, orig_eui_file + ".orig")
        shutil.copyfile(eui_cuc_file, orig_eui_file)
    subprocess.run([szip, 'a', modded_eui_zip, eui_path], stdout=null, stderr=null)
elif not eui_only:
    # Unzip EUI
    print("Unzipping EUI...")
    subprocess.run([szip, 'x', modded_eui_zip_path], stdout=null, stderr=null)

# Stop here if only EUI should be converted
if eui_only:
    if os.path.isdir(eui_path):
        shutil.rmtree(eui_path)
    quit()


# Unzip modpack zip
print("Unzipping Modpack...")
subprocess.run([szip, 'x', j(vanilla_packs_path, modpack_zip)], stdout=null, stderr=null)


# Manage mod files
for mod_file in g(mod_files, recursive = True):
    mod_file_path = mod_file.split(os.sep)
    mod_file_name = mod_file_path[len(mod_file_path) - 1]

    # IGE UI compat file
    if mod_file_name == ige_compat_file_name:
        print("Providing IGE-EUI-compat...")
        shutil.move(mod_file, mod_file + ".orig")
        shutil.copyfile(g(j(modsave_path, ige_compat_file_name + "*"))[0], mod_file)

    # Delete UI overwrite duplicates
    if mod_file_name in delete_file_names:
        print("Removing overwriting file " + mod_file_name + "...")
        os.remove(mod_file)

    # Find out if modcompat unit panel needed
    if mod_file_name in unit_panel_modcompat_file_names:
        print("UnitPanel modcompat need detected...")
        unit_panel_modcompat_needed = True

# Delete useless desktop.ini (Thanks True...)
ini_files = re.sub(r"\.\w+$", ".ini", mod_files)
for ini_file in g(ini_files, recursive = True):
    ini_file_path = ini_file.split(os.sep)
    ini_file_name = ini_file_path[len(ini_file_path) - 1]
    if ini_file_name == "desktop.ini":
        print("Removing useless desktop.ini (Thanks True)...")
        os.remove(mod_file)


# Get stuff from UI files
for ui_file in g(ui_files):
    with open(ui_file, 'r') as file:
        lines = file.readlines()
    ui_file_path = ui_file.split(os.sep)
    ui_file_name = ui_file_path[len(ui_file_path) - 1]
    print("Getting tags from " + ui_file_name + "...")
    load_tags[ui_file_name] = []
    for line in lines:
        if line.startswith(load_tag):
            load_tags[ui_file_name].append(line)

# Insert stuff into EUI files
for eui_file in g(eui_files):
    eui_file_path = eui_file.split(os.sep)
    eui_file_name = eui_file_path[len(eui_file_path) - 1]
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
shutil.move(eui_path, modpack_path)
print("Removing UI folder...")
shutil.rmtree(ui_path)

# Zip modpack folder
print("Zipping Modpack...")
subprocess.run([szip, 'a', modpack_name + "_EUI.7z", modpack_path], stdout=null, stderr=null)

#Finishing up
quit()