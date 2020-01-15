from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


import os
packet = io.BytesIO()
# create a new PDF with Reportlab
can = canvas.Canvas(packet, pagesize=letter)
pdfmetrics.registerFont(TTFont('Verdana Regular', '/Users/samralston/Desktop/print/VERDANA.TTF'))
can.setFont("Verdana Regular", 15)
can.drawString(70, 568, "Date")

can.drawString(640, 568, "H:")
can.drawString(670, 577, "time")
can.drawString(670, 557, "height")

can.drawString(740, 568, "L:")
can.drawString(770, 577, "time")
can.drawString(770, 557, "height")

can.drawString(522, 568, "Special")
can.save()

#move to the beginning of the StringIO buffer
packet.seek(0)
new_pdf = PdfFileReader(packet)
# read your existing PDF
existing_pdf = PdfFileReader(open("day.pdf", "rb"))
output = PdfFileWriter()
# add the "watermark" (which is the new pdf) on the existing page
page = existing_pdf.getPage(0)
page.mergePage(new_pdf.getPage(0))
output.addPage(page)
# finally, write "output" to a real file
outputStream = open("destination.pdf", "wb")
output.write(outputStream)
outputStream.close()

print(can.getAvailableFonts())


# `os.system("lpr -P brotherprint destination.pdf")`