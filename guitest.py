import PySimpleGUI as sg
from daysheetmaker import *


import queue
import threading
import time




def the_gui():
    
    



    sg.theme('SandyBeach')   # Add a touch of color

    layout = [
        [ 
            sg.Text("Enter day sheet date you want to start from: "),
            sg.CalendarButton(button_text="Select date", target="startdate", format="%Y-%m-%d"),
            sg.InputText(key="startdate")
            ],
            [
            sg.Text("Enter day sheet date you want to finish on: "),
            sg.CalendarButton(button_text="Select date", target="enddate", format="%Y-%m-%d"),
            sg.InputText(key="enddate")
            ],
            
            [
            sg.Text("Printer Name (leave blank by default.. unless not working, ask sam): "),
            sg.InputText(key="printername")
            ], 
            [ 
            sg.Submit(),
            sg.Text("___________________________________________________",key='pro')
        ]
    ]
    window = sg.Window('Day Sheet Creator',keep_on_top=True).Layout(layout)

    gui_queue = queue.Queue()

    
        # --------------------- EVENT LOOP ---------------------
    while True:
        event, values = window.Read(timeout=100)       # wait for up to 100 ms for a GUI event
        if event == "Submit":
            try:
                threading.Thread(target=guitaskgiver, args=(gui_queue,values,), daemon=True).start()
                # Tell user its printing... hopefully 
                window.Element('pro').Update("Printing your daysheets...")
            except Exception as e:
                print(e)
                # tell the user whats up 
                window.Element('pro').Update(e)
        # --------------- Check for incoming messages from threads  ---------------
        try:
            message =  gui_queue.get_nowait()
        except queue.Empty:             # get_nowait() will get exception when Queue is empty
            message = None              # break from the loop if no more messages are queued up

        # if message received from queue, display the message in the Window
        if message:
        # messages back from the thread from qu
            window.Element('pro').Update(message)

    # if user exits the window, then close the window and exit the GUI func
    window.Close()
        
    
    
    
def guitaskgiver(gui_queue,values):
    maker = daysheetmaker(values['startdate'],values['enddate'],values['printername'])
    maker.runner(gui_queue)
    
      
    

    
    
    
    
    
    
# event, values = window.Read()
# if event == "Submit":
#     print(values)
#     print(type(values["printername"]))

#     # PRINT PAGES 
#     window.Element('pro').Update("Printing")
#     maker = daysheetmaker(values['startdate'],values['enddate'],values['printername'])
#     maker.runner()
# if event is None or event == 'Cancel':
#     return None
            
            
            
the_gui()

