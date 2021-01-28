import time
from pathlib import Path
from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter.ttk import Progressbar
from datetime import datetime
import threading
import webbrowser
import IO
from Logger import *

# storing our setting file in the users appdata
home = str(Path.home()).replace('\\', '/') + '/'
import_settings = home + 'AppData/Roaming/ericmichelin/photo_import_settings.json'

# getting and formatting time
current_date = datetime.date(datetime.now())
fmt = "%Y-%m-%d %H:%M:%S"

# set settings for copying progress and cancellation
IO.copy_counter = [0, 0]
IO.kill_copy = False

# the threads used for copying local and remote files at the same time
global local_copy
global remote_copy
global refresh_thread


def update_folder(label, key):
    """Updates a label and saves that value in the settings file

    Parameters:
        label (Label): The GUI label to update sand save the path
        key (String): The key in the settings file to update the value of
    """

    new_dir = askdirectory() + '/'
    label.config(text=label.cget('text').split(' ', 1)[0] + ' ' + new_dir)
    IO.write_setting(import_settings, key, new_dir)


def open_settings():
    """Opens the photo_import_settings.json file in a text editor"""

    webbrowser.open(import_settings)


def refreshUI():
    """update the UI elements every second, in case a change was made directly in the settings file"""

    while IO.kill_copy is False:
        sd_card_folder_label.config(text='SD_Card: ' + IO.read_setting(import_settings, 'sd_card'))
        local_folder_label.config(text='Local: ' + IO.read_setting(import_settings, 'local'))
        remote_folder_label.config(text='Remote: ' + IO.read_setting(import_settings, 'remote'))
        last_import.config(text='Last import: ' + IO.read_setting(import_settings, 'import_history'))
        time.sleep(1)


def text_progress(current, total):
    """Opens the photo_import_settings.json file in a text editor

    Parameters:
        current (String): The currently completed progress
        total (String): The total amount

     Returns:
        progress (String): A formatted string with the current progress [current/total]
    """

    return '[' + format(current, '0' + str(len(str(total)))) + \
           '/' + \
           format(total, '0' + str(len(str(total)))) + ']'


def progress_update(progressbar, label, current, total):
    """For updating a progress bar and a text label based progress

    Parameters:
        progressbar (Progressbar): The progress bar to update
        label (Label): The Label to update progress as a string
        current (String): The currently completed progress
        total (String): The total amount
    """

    progressbar['value'] = current
    progressbar.update()
    label.config(text=text_progress(current, total))


def copy_files(self):
    """Verify inputs, copies new files"""

    global local_copy
    global remote_copy

    # to remove the dash from the import name if no name is provided (leaving just the date)
    if import_name.get() == '':
        new_folder = str(current_date)
    else:
        new_folder = str(current_date) + ' - ' + import_name.get()

    # checking if the directories are not empty, if so stop copy and return info message
    if sd_card_folder_label.cget('text').split(' ', 1)[1] == '' \
            or sd_card_folder_label.cget('text').split(' ', 1)[1] == '/':
        print_error_label('SD Card location is empty', info_text)
        return
    if local_folder_label.cget('text').split(' ', 1)[1] == '' \
            or local_folder_label.cget('text').split(' ', 1)[1] == '/':
        print_error_label('Local folder is empty', info_text)
        return
    if remote_folder_label.cget('text').split(' ', 1)[1] == '' \
            or remote_folder_label.cget('text').split(' ', 1)[1] == '/':
        print_error_label('Remote folder is empty', info_text)
        return

    # gets the list of files names of files created after the last import date
    new_files = IO.get_new_files_to_copy(sd_card_folder_label.cget('text').split(' ', 1)[1],
                                         IO.read_setting(import_settings, 'import_history'))

    # return if there are no new files
    if len(new_files) == 0:
        print_info_label('No new files to copy', info_text)
        return

    # create the new folders if needed (does nothing if they already exist)
    IO.create_folder(local_folder_label.cget('text').split(' ', 1)[1] + new_folder)
    IO.create_folder(remote_folder_label.cget('text').split(' ', 1)[1] + new_folder)

    # set the progress bar total value
    local_progress['maximum'] = len(new_files)
    remote_progress['maximum'] = len(new_files)

    # create out threads to do both the local and remote copy
    local_copy = threading.Thread(target=IO.super_copy,
                                  args=(
                                      sd_card_folder_label.cget('text').split(' ', 1)[1] + '/',
                                      local_folder_label.cget('text').split(' ', 1)[1],
                                      new_folder,
                                      new_files,
                                      0))
    remote_copy = threading.Thread(target=IO.super_copy,
                                   args=(sd_card_folder_label.cget('text').split(' ', 1)[1] + '/',
                                         remote_folder_label.cget('text').split(' ', 1)[1],
                                         new_folder,
                                         new_files,
                                         1))

    # start the threads (file copy)
    print_info_label('Starting copy', info_text)
    local_copy.start()
    remote_copy.start()

    # while the copy is i progress, update the progress bar and text
    while (local_copy.is_alive() or remote_copy.is_alive()) and IO.kill_copy is False:
        progress_update(local_progress, local_text_progress, IO.copy_counter[0], len(new_files))
        progress_update(remote_progress, remote_text_progress, IO.copy_counter[1], len(new_files))
        time.sleep(0.1)

    # do one file update to progress after copy complete
    progress_update(local_progress, local_text_progress, IO.copy_counter[0], len(new_files))
    progress_update(remote_progress, remote_text_progress, IO.copy_counter[1], len(new_files))

    # update the info depending on if the import was cancelled or completed naturally
    if IO.kill_copy:
        print_info_label('Copy Cancelled', info_text)
    else:
        print_info_label('Copy Finished', info_text)
        IO.write_setting(import_settings, 'import_history', (str(datetime.now().strftime(fmt))))
        last_import.config(
            text='Last import: ' + IO.read_setting(import_settings, 'import_history'))


def close():
    """Quits the application stopping after the currently in progress file completes"""

    global local_copy
    global remote_copy

    IO.kill_copy = True
    print_info_label('Stopping', info_text)
    refresh_thread.join()

    # this try is to handle if no copy was done
    try:
        local_copy.join()
        remote_copy.join()

    except NameError:
        ''

    window.quit()


# set up the root window
window = Tk()
window.geometry('455x190')
window.minsize('455', '190')
window.resizable(1, 0)
window.config(bg='#ffffff')
window.title('Photo Import & Backup')
window.protocol("WM_DELETE_WINDOW", close)

# set the main frame that contains most of the UI
main = Frame(window, bg='#ffffff')
main.pack(side='top')

last_import = Label(
    main,
    text="Last import: YYYY-MM-DD hh:mm:ss",
    bg='#ffffff'
)
last_import.grid(row=0, column=0, columnspan=4)

settings_button = Button(
    main,
    text="Settings",
    command=open_settings,
    bg='#6200ee',
    fg='#ffffff'
)
settings_button.grid(row=0, column=4, padx=1)

import_name_frame = Frame(main, bg='#ffffff')
import_name_frame.grid(row=1, column=0, columnspan=2)

import_name_label = Label(
    import_name_frame,
    text="Import Name",
    bg='#ffffff',
    padx=5,
)
import_name_label.grid(row=0, column=0, sticky='E')

import_name = Entry(
    import_name_frame,
    text="Folder/Import Name",
    bg='#ffffff'
)
import_name.grid(row=0, column=1, sticky='W', padx=5, pady=5)

copy_button = Button(
    main,
    text="Start Copy",
    bg='#6200ee',
    fg='#ffffff',
    padx=3,
    command=lambda: copy_files('self')

)
copy_button.grid(row=1, column=2, sticky='W', padx=5, pady=5)

sd_card_folder_label = Label(
    main,
    text="SD_Card: ",
    bg='#ffffff'
)
sd_card_folder_label.grid(row=2, column=0, columnspan=2, sticky='W', padx=5, pady=5)

sd_card_folder_change_button = Button(
    main,
    text='Change',
    bg='#6200ee',
    fg='#ffffff',
    padx=10,
    command=lambda: update_folder(sd_card_folder_label, 'sd_card')
)
sd_card_folder_change_button.grid(row=2, column=2, sticky='E', padx=5, pady=5)

local_folder_label = Label(
    main,
    text='Local: path/to/local',
    bg='#ffffff'
)
local_folder_label.grid(row=3, column=0, columnspan=2, sticky='W', padx=5, pady=5)

remote_folder_label = Label(
    main,
    text='Remote: path/to/remote',
    bg='#ffffff'
)
remote_folder_label.grid(row=4, column=0, columnspan=2, sticky='W', padx=5, pady=5)

local_folder_change_button = Button(
    main,
    text='Change',
    bg='#6200ee',
    fg='#ffffff',
    padx=10,
    command=lambda: update_folder(local_folder_label, 'local')
)
local_folder_change_button.grid(row=3, column=2, sticky='E', padx=5, pady=5)

remote_folder_change_button = Button(
    main,
    text='Change',
    bg='#6200ee',
    fg='#ffffff',
    padx=10,
    command=lambda: update_folder(remote_folder_label, 'remote')
)
remote_folder_change_button.grid(row=4, column=2, sticky='E', padx=5, pady=5)

local_progress = Progressbar(
    main,
    orient=HORIZONTAL,
    length=100,
    maximum=1,
    value=0,
    mode="determinate"
)
local_progress.grid(row=3, column=3, sticky='E')

remote_progress = Progressbar(
    main,
    orient=HORIZONTAL,
    length=100,
    maximum=1,
    value=0,
    mode="determinate"
)
remote_progress.grid(row=4, column=3, sticky='E')

local_text_progress = Label(
    main,
    text="[   /   ]",
    bg='#ffffff',
    padx=5
)
local_text_progress.grid(row=3, column=4, sticky='W')

remote_text_progress = Label(
    main,
    text="[   /   ]",
    bg='#ffffff',
    padx=5
)
remote_text_progress.grid(row=4, column=4, sticky='W')

info_text = Label(
    window,
    text="",
    bg='#ffffff',
    padx=5
)
info_text.pack(side='left')

if __name__ == '__main__':
    sd_card_folder_label.config(text='SD_Card: ' + IO.read_setting(import_settings, 'sd_card'))
    local_folder_label.config(text='Local: ' + IO.read_setting(import_settings, 'local'))
    remote_folder_label.config(text='Remote: ' + IO.read_setting(import_settings, 'remote'))
    last_import.config(text='Last import: ' + IO.read_setting(import_settings, 'import_history'))
    window.bind('<Return>', copy_files)

    refresh_thread = threading.Thread(target=refreshUI, args=())
    refresh_thread.start()

    window.mainloop()
