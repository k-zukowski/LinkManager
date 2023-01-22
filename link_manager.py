import os
import sys
import wget
import lxml
import Utils
import shutil
import requests
import re as regex
import logging as log
import PySimpleGUI as Gui
from tqdm import tqdm
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.request import urlopen
from PropertiesHandler import PropertiesHandler

BLACK_CLR = "Black"
ph = PropertiesHandler()
services = ph.get_services().split(" ")
iter_file_name = ".iter.txt"
Utils.create_iteration(iter_file_name)
iteration = open(iter_file_name, "r").read()

log.basicConfig(filename='Zlog.log',
                level=log.DEBUG,
                format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')
log.debug("Start")
log.debug("Iteration = " + iteration)
layout = [[Gui.Text('Choose type', size=(15, 1), font='Lucida', justification='left', background_color=BLACK_CLR),
           Gui.Combo([services[0], services[1]],
                     default_value=services[0], key='type')],

          [Gui.Text('Choose user id ', size=(15, 1), font='Lucida', justification='left', background_color=BLACK_CLR),
           Gui.InputText(size=15, key='id', disabled=False, default_text=ph.get_default_id())],

          [Gui.Text('From', size=(15, 1), font='Lucida', justification='left', background_color=BLACK_CLR),
           Gui.InputText(size=15, key='from', default_text='0')],

          [Gui.Text('To', size=(15, 1), font='Lucida', justification='left', background_color=BLACK_CLR),
           Gui.InputText(size=15, key='to', default_text='0')],

          [Gui.Text("Do you want to download the files ?", size=35, font="Lucida", justification="left",
                    background_color=BLACK_CLR)],
          [Gui.Checkbox(size=(20, 50), text="y/N", key="check", background_color=BLACK_CLR, enable_events=True)],

          [Gui.Text('Where to?', background_color=BLACK_CLR, auto_size_text=True),
           Gui.In(size=(55, 1), enable_events=True, key='-FOLDER-', disabled=True),
           Gui.FolderBrowse(key='browse', disabled=True, initial_folder=str(Path.home() / "Downloads"))],

          [Gui.Button('SAVE', font=('Times New Roman', 12), key="save"), Gui.Button('CANCEL',
                                                                                    font=('Times New Roman', 12),
                                                                                    key="cancel")]]

Gui.theme('Black')
win = Gui.Window('Link Manager', layout, size=(570, 300), keep_on_top=True,
                 location=(int(1920 / 2 - 570 / 2), int(1080 / 2 - 300 / 2)), icon="Images/icon.ico")
folder = ""
while True:
    e, v = win.read()
    ch = v['check']
    if not ch:
        win.find_element('-FOLDER-').Update(disabled=True)
        win.find_element('browse').Update(disabled=True)
        folder = "blank"
        win.Refresh()
    else:
        win.find_element('-FOLDER-').Update(disabled=False)
        win.find_element('browse').Update(disabled=False)
        folder = v['-FOLDER-']
        win.Refresh()
    if e == 'save':
        break
    if e in (Gui.WIN_CLOSED, 'Exit'):
        log.debug("Exited. Exiting...")
        sys.exit("Exited. Exiting...")
    if e == 'cancel':
        log.debug("Cancelled. Exiting...")
        sys.exit("Cancelled. Exiting...")

win.close()
service = v['type'].lower()
userId = int(v['id'])
start = int(v['from'])
end = int(v['to'])

log.debug("Service => " + service +
          ",userId => " + str(userId) +
          ",start => " + str(start) +
          ",end => " + str(end) +
          ",folder => " + str(folder))

address_offset = list()
for i in range(start, end + 1, 50):
    address_offset.append(i)

main_addresses = list()
for offset in address_offset:
    text = "{main}/{service}/user/{userid}?o={offset}".format(main=ph.get_main(), service=service, userid=str(userId),
                                                              offset=str(offset))
    main_addresses.append(text)
    log.debug(text)

red_links_file_name = "{name}_{iteration}.txt".format(name="RedLinks", iteration=iteration)
red_links_file = open(red_links_file_name, "a", encoding="utf-8")
data_file_name = "{name}_{iteration}.txt".format(name="Data", iteration=iteration)
data_file = open(data_file_name, "a", encoding="utf-8")
links_file_name = "{name}_{iteration}.txt".format(name="Links", iteration=iteration)
links_file = open(links_file_name, "a", encoding="utf-8")

pbar_page = tqdm(main_addresses, position=0, leave=True)
for main_address in pbar_page:
    pbar_page.set_description("Fetching links of posts from page")
    log.debug("Current main address = " + str(main_address))
    main_source = requests.get(main_address).text
    sub_addresses = Utils.regex_main(main_source, str(userId), service)
    sub_addresses = list(map((lambda x: ph.get_main() + x), sub_addresses))
    pbar_post = tqdm(sub_addresses, position=0, leave=True)
    for sub_address in pbar_post:
        pbar_post.set_description("Fetching links of media from posts")
        log.debug("Current sub address " + str(sub_address))
        sub_source_raw = urlopen(sub_address).read().decode('utf-8')
        sub_source_pretty = BeautifulSoup(sub_source_raw, features="lxml").prettify()
        data_file.write(sub_source_pretty)
        links = (regex.findall(r'=\"/(?!static|thumbnail).*\.(?:gif|jpg|png)', sub_source_pretty))
        links = list(set(map((lambda x: ph.get_main() + x[2:len(x)] if (x.startswith('=\"/data/'))
        else ph.get_data() + x[2:len(x)]), links)))
        for link in links:
            links_file.write(link + '\n')
            log.debug("Adding {all_link} to links".format(all_link=str(link)))
        log.debug("Current links = {linesep} {links}".format(linesep=os.linesep, links=', '.join(map(str, links))))

        # Also search for other links i.e. red
        red_links = regex.findall(r"href=\"https://www\.(?:" + ph.get_red() + "|sthelse).*\"", sub_source_raw)
        red_links = list(set(map((lambda x: x[6:-1]), red_links)))
        if len(red_links) > 0:
            for red_link in red_links:
                red_sub_source = requests.get(red_link).text
                red_sub_source_pretty = BeautifulSoup(red_sub_source, "html.parser").prettify()
                red_regex = regex.findall(r"content=\"https.*\.(?:mp4|webm)\"", red_sub_source_pretty)
                red_links_w = list()
                for red_regex_sub_link in red_regex:
                    if "mobile" not in red_regex_sub_link:
                        red_links_w.append(red_regex_sub_link[9:-1])
                for red_link_w in red_links_w:
                    red_links_file.write(red_link_w + os.linesep)
        log.debug("End sub")
    log.debug("End main")
data_file.close()
links_file.close()
red_links_file.close()
problematic_links_file_name = "{name}_{iteration}.txt".format(name="Problematic_links", iteration=iteration)
problematic_links_file = open(problematic_links_file_name, "a", encoding="utf-8")
if folder != "blank":
    log.debug("Start downloading")
    with open(links_file_name) as f:
        lines = f.read().splitlines()
    pbar_major = tqdm(lines, position=0, leave=True)
    for link_dl in pbar_major:
        pbar_major.set_description("Downloading major")
        # try to download
        try:
            wget.download(link_dl, out=folder)
            log.debug("Downloaded => " + str(link_dl))
        except Exception as e:
            log.debug("Caught in exception => " + str(link_dl))
            log.exception(e)
            # try to fix the link
            pattern_exception = regex.compile(r"\?f=png", regex.IGNORECASE)
            link_exception = pattern_exception.sub("", link_dl)
            # try again
            try:
                wget.download(link_exception, out=folder)
            except Exception as ex:
                problematic_links_file.write(link_exception)
                log.exception(ex)
                log.error("Could not download link => " + str(link_exception))
                continue
            log.debug("Downloaded after exception=> " + str(link_exception))

    log.debug("Ended downloading main")
    with open(red_links_file_name) as red_links_dl:
        red_lines = red_links_dl.read().splitlines()
        pbar_minor = tqdm(red_lines, position=0, leave=True)
        for red_link_dl in pbar_minor:
            pbar_minor.set_description("Downloading minor")
            red_file_name = red_link_dl.split('/')[-1]
            response = requests.get(red_link_dl, stream=True)
            with open(red_file_name, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            shutil.move(str(os.getcwd() + "/" + red_file_name), str(folder))
    problematic_links_file.close()
    Utils.move_links(folder=folder, iteration=iteration)
else:
    log.debug("Skipping downloading")
Utils.delete_tmp_files()
Utils.update_iteration(iteration=iteration, iter_file_name=iter_file_name)
log.debug("Done")
log.debug("###########################################################################################################")
