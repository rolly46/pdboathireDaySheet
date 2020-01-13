import PySimpleGUI as sg
from daysheetmaker import *


sg.theme('SandyBeach')   # Add a touch of color
def demo_date_picker():
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
            sg.Cancel(), 
            sg.Text("___________________________________________________",key='pro')
        ]
    ]
    
    window = sg.Window('Day Sheet Creator',keep_on_top=True).Layout(layout)

    while True:
        event, values = window.Read()
        if event == "Submit":
            print(values)
            print(type(values["printername"]))

            # PRINT PAGES 
            window.Element('pro').Update("Printing")
            maker = daysheetmaker(values['startdate'],values['enddate'],values['printername'])
            maker.runner()
        if event is None or event == 'Cancel':
            return None
        
        
        
demo_date_picker()

