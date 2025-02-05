from fpdf import FPDF
import json
from datetime import datetime
import webbrowser
from PIL import Image
import math
import sys
import os
import glob
from operator import itemgetter
import tkinter as tk
from tkinter import filedialog



resize_height = 1050
resize_width = 670

#spacing between cards
hori_spacing = 100
vert_spacing = 10   #best between 0 to 50, otherwise images might fall off the page



script_path=os.path.abspath(__file__)
script_dir=os.path.split(script_path)[0]
rel_path="pack/*"
abs_file_path=os.path.join(script_dir, rel_path)

pdf=FPDF()
pdf.add_page()
pdf.add_font('FreeSans', '', 'FreeSans.ttf', uni=True)
pdf.set_font('FreeSans','',10)


#sgfile=open(abs_file_path, "r")
#sg=sgfile.readlines()
#sgfile.close()

#for pack in packs:
#    pack["date"]=datetime.strptime(pack["date_release"], '%Y-%m-%d')
packs = {}


#for file in glob.glob(abs_file_path):
#    allfiles=open(file, "r")
#    list = json.load(allfiles)
#    allfiles.close()
#    cards.append(list)
#    pack = file.split('\\')
 #   pack = pack[-1]
#    pack = pack.split('.')
 #   pack = pack[0]
 #   packs[pack]=file
#    #pdf.multi_cell(150,5,pack,1,0)

for file in glob.glob(abs_file_path):
    pack = file.split('\\')
    pack = pack[-1]
    pack = pack.split('.')
    pack = pack[0]
    packs[pack]=file


startup_cycles = ["System Gateway", "System Update 2021", "Borealis"]


cyclefile = open("cycles.json", "r")
cycles = json.load(cyclefile)
cyclefile.close()

startup_codes = []


for cycle in cycles:
    if cycle['name'] in startup_cycles:
        startup_codes.append(cycle['code'])
   
    
packsfile = open("packs.json", "r")
packslist = json.load(packsfile)
packsfile.close()

startup_packs =[]


for pack in packslist:
    if pack['cycle_code'] in startup_codes:
        startup_packs.append(pack['code'])
   
startup_packs.remove('msbp')

cardlistbypack = []



for file in startup_packs:
    cardfile = open(packs[file],"r", encoding= 'utf-8')
    cards=json.load(cardfile)
    cardfile.close()
    cardlistbypack.append(cards)

cardlist = []

for list in cardlistbypack:
    for card in list:
        cardlist.append(card)


cardkeys = {"HQ":"HQ", "R&D":"R&D", "Archives":"Archives"}

for card in cardlist:
    cardkeys[card['title']]=card['code']

#pdf.multi_cell(150,5,str(cardkeys),1,0)


root = tk.Tk()
root.withdraw()
image_path = filedialog.askdirectory()
deckfile = open('decklist.txt', encoding='utf-8')
decklist = deckfile.readlines()
deckfile.close()

marks = ["33019","33012","33012","33011","33081","33015"]
mark_targets = ["HQ", "R&D", "Archives"]
proxy_list = []
file_match = []
file_list = sorted(glob.glob(image_path + '/*.jpg'))
file_match_index = 0

for filename in file_list:
    file = filename.replace(image_path, "")
    card = file.replace('.jpg',"")
    card = card.replace("\\", "")
    file_match.append(card)

log = open("decklog.txt", "a", encoding="utf-8")
log.write(str(cardkeys)+"\n")
log.write(str(file_match)+"\n")

mark_exists=0

for card in decklist:
    #log.write(card)
    split = card.split()
    count = split[0]
    card = card.replace(count+" ", "")
    card = card.replace("\n","")
    copies = range(int(count))
    card_index = file_match.index(cardkeys[card])
    filename = file_list[card_index]
    if cardkeys[card] in marks and mark_exists==0:
        mark_exists+=1
        for mark in mark_targets:
            mark_index = file_match.index(cardkeys[mark])
            mark_name = file_list[mark_index]
            mark_picture = Image.open(mark_name)
            proxy_list.append(mark_picture)
        
    #pdf.multi_cell(150,5,card,1,0)

    for item in copies:
        card_picture = Image.open(filename)
        log.write(str(card_index)+"\n")
        log.write(filename+"\n")
        proxy_list.append(card_picture)
        pdf.multi_cell(150,5,str(card),1,0)
   
log.close()

proxy_index = 0
sheet_list = []
page_count = math.ceil(float(len(proxy_list))/9.0)

for _ in range (0, int(page_count)):
    y_offset = 200
    x_offset = 200
    sheet = Image.new('RGB', ((x_offset+hori_spacing)*2+resize_width*3, (y_offset+vert_spacing)*2+resize_height*3), (255, 255, 255))
    rows = [Image.new('RGB', ((x_offset+hori_spacing)*2+resize_width*3, resize_height), (255, 255, 255))] * 3
    for row in rows:
        x_offset=200
        for j in range (proxy_index,proxy_index+3):
            if j >= len(proxy_list):
                break
            row.paste(proxy_list[j], (x_offset,0))
            x_offset += resize_width + hori_spacing
        sheet.paste(row, (0, y_offset))
        y_offset += resize_height+vert_spacing
        proxy_index+=3
        if proxy_index >= len(proxy_list):
            break
    sheet_list.append(sheet)

sheet_list[0].save('decklist.pdf', quality=90, resolution=600, optimize=True, save_all=True, append_images=sheet_list[1:])




#pdf.multi_cell(150,5,str(cardlist),1,0)
pdf.output('deck.pdf')
