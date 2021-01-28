import os
import json
from datetime import datetime
from pathlib import Path
from shutil import copy2
from Logger import print_warn, print_info, print_error

# gets the users home folder
home = str(Path.home()).replace('\\', '/') + '/'

# date format
fmt = "%Y-%m-%d %H:%M:%S"

global copy_counter
global kill_copy


def get_last_date_from_file(file_name):
    """The file to read the last line(date) from

    Parameters:
        file_name (String): The file path and name

     Returns:
        last_file_date (String): the last date in the file (last line)
    """

    try:
        with open(file_name, 'r') as f:
            lines = f.read().splitlines()
            last_line = lines[-1]
            last_file_date = last_line
            f.close()
            print_info('Last import was: ' + last_file_date)
            return last_file_date
    except FileNotFoundError:
        print_warn('Could not find last time of import (file missing), import all since 2000')
        return '2000-01-01 00:00:00'
    except IndexError:
        print_warn('Could not find last time of import (file empty), import all since 2000')
        return '2000-01-01 00:00:00'


def print_this_date_to_file(file_name):
    """The file to write the current date to

    Parameters:
        file_name (String): The file path and name
    """

    current_date_time = datetime.now()
    try:
        f = open(file_name, 'a')
    except FileNotFoundError:
        f = open(file_name, 'x')
        f.write(str(current_date_time.strftime(fmt)) + '\n')
    f.close()


def create_folder(location):
    """Creates a folder at the given path

    Parameters:
        location (String): The file path of the folder to create
    """

    try:
        os.mkdir(location)
    except FileExistsError:
        'Folder exists'
    else:
        print_info('Created the folder: ' + location)


def get_new_files_to_copy(location, last_import):
    """Returns a list of files names created after the given last_import date

    Parameters:
        location (String): The folder of all the images to copy
        last_import (String): The file path and name

     Returns:
        last_file_date (String): the last date in the file (last line)
    """

    all_files = []
    new_files = []
    for (dirpath, dirnames, filenames) in os.walk(location):
        all_files.extend(filenames)
        break

    for file in all_files:
        f_time_epoch = os.stat(location + file).st_mtime
        f_time = datetime.fromtimestamp(f_time_epoch)
        if int(f_time_epoch) >= int(datetime.strptime(last_import, fmt).timestamp()):
            new_files.append(file)

    print_info('There are ' + str(len(new_files)) + ' files to import')
    return new_files


def super_copy(original_location, copy_location, folder_name, files, counter):
    """Uses the copy2 function to copy files and updates the given global variable after each loop to track progress

    Parameters:
        original_location (String): the folder containing the files to copy
        copy_location (String): the folder to copy the files to
        folder_name (String): the name of the new folder the copies are going in
        files (List): a list of files names
        counter (String): Which global counter variable to update
    """

    for f in files:
        copy2(original_location + f, copy_location + folder_name + '/' + f)
        copy_counter[counter] += 1
        if kill_copy:
            break


def read_setting(file, key):
    """Reads a value from the settings file bas

    Parameters:
        file (String): the path of the settings file
        key (String): the key you want the value of

    returns: the value of the given key
    """

    try:
        with open(file) as json_data:
            settings = json.load(json_data)

        for k, v in settings.items():
            if k == key:
                return str(v)

        print_error('Could not find key: "' + key + '" in file "' + file + '"')
        return ''
    except FileNotFoundError:
        create_empty_settings(file)
        read_setting(file, key)
        return ''


def write_setting(file, key, value):
    """Writes a key value to a file

    Parameters:
        file (String): the path of the settings file
        key (String): the key you want to write a new value to
        value (String): the new value to write
    """

    with open(file) as json_data:
        settings = json.load(json_data)

    exists = False
    for k in settings:
        if k == key:
            exists = True

    if exists:
        update = {key: value}
        settings.update(update)
        with open(file, 'w') as json_data2:
            json.dump(settings, json_data2, indent=4)
        print_info('Updated key: "' + key + '" with value: "' + value + '"')
    else:
        print_error('Could not find key: "' + key + '" in file: ' + file + '"')


def create_empty_settings(file):
    """Create a settings file with default values

    Parameters:
        file (String): the settings file path
    """

    data = {
        "sd_card": "",
        "local": home + 'Pictures/',
        "remote": "",
        "import_history": "2020-01-01 00:00:00"
    }
    try:
        with open(file, 'w') as json_data:
            json.dump(data, json_data, indent=4)
        print_info('Created settings file: ' + file + '"')
    except FileNotFoundError:
        create_folder(file.rsplit('/', 1)[0])
        create_empty_settings(file)
