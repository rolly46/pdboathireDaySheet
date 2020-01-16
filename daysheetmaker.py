#scraping bom 
import requests
from bs4 import BeautifulSoup
import datetime
#making image
# from PIL import Image
# from PIL import ImageDraw
# from PIL import ImageFont
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
#print
import os




class daysheetmaker:
    
    def __init__(self,strstartdate, strenddate, printername):
        self.strstartdate = strstartdate
        self.strenddate = strenddate
        self.printername = printername
    

    def runner(self,qu):
        
        #watermark function
        def watermark_text(info, tidestatus):
            packet = io.BytesIO()
            # create a new PDF with Reportlab
            can = canvas.Canvas(packet, pagesize=letter)
            pdfmetrics.registerFont(TTFont('Verdana Regular', '/Users/samralston/Desktop/print/VERDANA.TTF'))
            can.setFont("Verdana Regular", 15)
            can.drawString(57, 568, str(info[0]))
            can.drawString(640, 568, "H:")
            can.drawString(740, 568, "L:")
            can.setFont("Verdana Regular", 10)
            # high tides
            can.drawString(660, 577, info[3])
            can.drawString(660, 562, info[4])
            # low tides
            can.drawString(760, 577, info[1])
            can.drawString(760, 562, info[2])
            if tidestatus:
                can.drawString(522, 568, "Special")
            can.save()

            #move to the beginning of the StringIO buffer
            packet.seek(0)
            new_pdf = PdfFileReader(packet)
            # read your existing PDF
            existing_pdf = PdfFileReader(open("/Users/samralston/Desktop/print/day.pdf", "rb"))
            output = PdfFileWriter()
            # add the "watermark" (which is the new pdf) on the existing page
            page = existing_pdf.getPage(0)
            page.mergePage(new_pdf.getPage(0))
            page.rotateCounterClockwise(90)
            output.addPage(page)
            # finally, write "output" to a real file
            outputStream = open("dayEdit.pdf", "wb")
            output.write(outputStream)
            outputStream.close()
        
        # actual work
        try:
            

            # date in yyyy/mm/dd format time that matters
            beginningofday = datetime.time(6, 0, 0) 
            endofday = datetime.time(18, 0, 0)

            startdate = datetime.datetime.strptime(self.strstartdate, "%Y-%m-%d").date()
            enddate = datetime.datetime.strptime(self.strenddate, "%Y-%m-%d").date()

            numOfDays = ((enddate-startdate).days) + 1


            #loop all this with dates 
            for n in range(numOfDays):
                
                #grabdata
                lowtidesarray = []
                hightidesarray = []
                singletide = False
                currentdate = (startdate + datetime.timedelta(days=n)).strftime("%Y-%m-%d")
                # tell the user current date being printed 
                qu.put("Queuing daysheet with the date, " + currentdate + "...")
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

            #  Apply watermarking
                watermark_text(finalarray, singletide)
                
                
                
            #print 
                if self.printername != '':
                    os.system("lpr -P "+ self.printername  + " dayEdit.pdf")
                else:
                    os.system("lpr -o landscape -P brotherprint dayEdit.pdf")
             
            qu.put("All daysheets qeued. They should now be printing.")
        
        except Exception as e:
             qu.put("Error: "+ str(e))



                



