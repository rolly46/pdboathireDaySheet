#scraping bom 
import requests
from bs4 import BeautifulSoup
import datetime
#making image
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
#print
import os

import PySimpleGUI as sg
import queue
import threading
import time

class daysheetmaker:
    
    def __init__(self,strstartdate, strenddate, printername):
        self.strstartdate = strstartdate
        self.strenddate = strenddate
        self.printername = printername
    
 
    gui_queue = queue.Queue()
    def runner(self):



        # date in yyyy/mm/dd format time that matters
        beginningofday = datetime.time(6, 0, 0) 
        endofday = datetime.time(18, 0, 0)

        # varibles 
        picin = '/Users/samralston/Desktop/print/daysheet.png'
        picout = '/Users/samralston/Desktop/print/editdaysheet.png'


        # strstartdate = "2020-01-01"
        # strenddate = "2020-12-31"

        startdate = datetime.datetime.strptime(self.strstartdate, "%Y-%m-%d").date()
        enddate = datetime.datetime.strptime(self.strenddate, "%Y-%m-%d").date()


        numOfDays = ((enddate-startdate).days) 


        #loop all this with dates 
        for n in range(numOfDays):

            #grabdata
            lowtidesarray = []
            hightidesarray = []
            singletide = False
            currentdate = (startdate + datetime.timedelta(days=n)).strftime("%Y-%m-%d")
            # print(currentdate)
            URL = 'http://www.bom.gov.au/australia/tides/scripts/getTidesTable.php?type=tide&aac=QLD_TP023&date='+currentdate+'&days=1&region=QLD&offset=0&offsetName=&tz=Australia%2FBrisbane&tz_js=AEST'
            page = requests.get(URL)
            soup = BeautifulSoup(page.content, 'html.parser')
            lowTides = soup.findAll("td", {"class": "localtime low-tide"})
            heightlowTides = soup.findAll("td", {"class": "height low-tide"})

            for index,lowtide in enumerate(lowTides):
                lowtidesarray.append((lowtide.text, heightlowTides[index].text))
            highTides = soup.findAll("td", {"class": "localtime high-tide"})
            heighthighTides = soup.findAll("td", {"class": "height high-tide"})
            for index,hightide in enumerate(highTides):
                hightidesarray.append((hightide.text, heighthighTides[index].text))
            print(lowtidesarray)
            print(hightidesarray)
            # add actual date in 
            #convert arrays from string to datetime
            for index,inlowtides in enumerate(lowtidesarray):
                date_time_str =  inlowtides[0]
                date_time_obj = datetime.datetime.strptime(date_time_str, '%I:%M %p')
                lowtidesarray[index] = (date_time_obj, inlowtides[1])
            for index,inhightides in enumerate(hightidesarray):
                date_time_str =  inhightides[0]
                date_time_obj = datetime.datetime.strptime(date_time_str, '%I:%M %p')
                hightidesarray[index] = (date_time_obj, inhightides[1])    

            # flag 1 tide a day  (before we trim the uninportant one)
            if len(hightidesarray) == 1:
                singletide = True

            # find the low tide that matters (unless theres only 1 high/low in the day)
            for index,inlowtides in enumerate(lowtidesarray):
                if ((inlowtides[0].time() < beginningofday) or (inlowtides[0].time() > endofday)) and len(lowtidesarray) != 1:
                    del lowtidesarray[index]
            # find the high tide that matters 
            for index,inhightides in enumerate(hightidesarray):
                if ((inhightides[0].time() < beginningofday) or (inhightides[0].time() > endofday)) and len(hightidesarray) != 1:
                    del hightidesarray[index]

                #      orginal ->   finalarray = [(startdate + datetime.timedelta(days=n)).strftime('%A %d %B %Y'),(lowtidesarray[0][0].strftime('%I:%M %p')),lowtidesarray[0][1],hightidesarray[0][0].strftime('%I:%M %p'),hightidesarray[0][1]]

            print(lowtidesarray)
            print(hightidesarray)
            # create final array
            # [currentdate, low tide time, low tide height, high tide time, high tide depth]
            if len(lowtidesarray) == 0:
                lowtidesarray = [('n/a','n/a')]
                finalarray = [(startdate + datetime.timedelta(days=n)).strftime('%A %d %B %Y'),(lowtidesarray[0][0]),lowtidesarray[0][1],hightidesarray[0][0].strftime('%I:%M %p'),hightidesarray[0][1]]
                singletide = True
            elif len(hightidesarray) == 0:
                hightidesarray = [('n/a','n/a')]
                finalarray = [(startdate + datetime.timedelta(days=n)).strftime('%A %d %B %Y'),(lowtidesarray[0][0].strftime('%I:%M %p')),lowtidesarray[0][1],hightidesarray[0][0],hightidesarray[0][1]]
                singletide = True
            else:
                finalarray = [(startdate + datetime.timedelta(days=n)).strftime('%A %d %B %Y'),(lowtidesarray[0][0].strftime('%I:%M %p')),lowtidesarray[0][1],hightidesarray[0][0].strftime('%I:%M %p'),hightidesarray[0][1]]




            #watermark function
            def watermark_text(input_image_path,
                            output_image_path,
                            info, pos1,pos2,pos3,pos4,pos5,pos6, tidestatus):
                photo = Image.open(input_image_path)
            
                # make the image editable
                drawing = ImageDraw.Draw(photo)
                green = (0, 153, 0)
                font = ImageFont.truetype("/Users/samralston/Desktop/print/Roboto-Black.ttf", 50)
                # date
                drawing.text(pos1, str(info[0]), fill=green, font=font)
                # L
                drawing.text((3100,65), "L:", fill=green, font=font)
                # L stats
                drawing.text(pos2, info[1], fill=green, font=font)
                drawing.text(pos3, info[2], fill=green, font=font)
                # H
                drawing.text((2650,65), "H:", fill=green, font=font)
                # H stats
                drawing.text(pos4, info[3], fill=green, font=font)
                drawing.text(pos5, info[4], fill=green, font=font)
                if tidestatus:
                    drawing.text(pos6, "Weird Tides Today", fill=green, font=font)
                # view image
                # photo.show()
                photo.save(output_image_path)
                
            watermark_text(picin,picout, finalarray, (300,65),(3200,35),(3200,95),(2750,35),(2750,95),(2300,120), singletide)

            #print 
            # if self.printername != '':
            #     os.system("lpr -P "+ self.printername  + " editpo.png")
            # else:
            #     os.system("lpr -P brotherprint editpo.png")
            
    gui_queue.put('** Done **')



            
        

