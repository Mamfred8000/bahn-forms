from PyPDF2 import PdfReader, PdfWriter
from Crypto.Cipher import AES
import pandas as pd
import numpy as np

def init():
    global pdf_input_file
    pdf_input_file = "Fahrgastrechte-Formular.pdf"
    global pdf_reader
    pdf_reader = PdfReader(pdf_input_file)
    global pdf_writer
    pdf_writer = PdfWriter()
    global delay_table
    delay_table = 'zug_verspätungen.xlsx'

def write_dict(d, indent=0):
    for key, value in d.items():
        txt_writer.write('\t' * indent + str(key) + '\n')
        if isinstance(value, dict):
            write_dict(value, indent+1)
        else:
            txt_writer.write('\t' * (indent+1) + str(value) + '\n')

def get_fields():
    global txt_file
    global txt_writer
    txt_file = "fields.txt"
    fields_dict = pdf_reader.get_fields()
    with open(txt_file, "w+") as txt_writer:
        write_dict(fields_dict)

def read_table():
    df = pd.read_excel(delay_table)
    df = df.loc[df['Status'] == 'test']
    df['Datum'] = df['Datum'].dt.strftime('%Y-%m-%d')
    ls = [
            df['Datum'],#.dt.day.to_list(),       #Reisedatum Tag (TT)
            'Test',       #Reisedatum Monat (MM)
            'Test',       #Reisedatum Jahr (JJ)
            'Test',     #Startbahnhof
            'Test',     #Abfahrt laut Fahrplan Stunde (HH)
            'Test',     #Abfahrt laut Fahrplan Minute (MM)
            'Test',     #Zielbahnhof
            'Test',     #Ankunftszeit laut Fahrplan Stunde (HH)
            'Test',     #Ankunftszeit laut Fahrplan Minute (MM)
            'Test',    #Ankunftsdatum Tag (TT)
            'Test',    #Ankunftsdatum Monat (MM)
            'Test',    #Ankunftsdatum Jahr (JJ)
            'Test',    #Angekommen bin ich mit Zug Zugart (ICE/IC/RE/RB etc.)
            'Test',    #Angekommen bin ich mit Zug Zugnummer
            'Test',    #tatsächliche Ankunft Stunde (HH)
            'Test',    #tatsächliche Ankunft Minute (MM)
            'Test',    #Erster verspäteter/ausgefallener Zug Zugart (ICE/IC/RE/RB etc.)
            'Test',    #Erster verspäteter/ausgefallener Zug Zugnummer
            'Test',    #Erster verspäteter/ausgefallener Zug Abfahrt laut Fahrplan Stunde (HH)
            'Test'     #Erster versp�teter/ausgefallener Zug � Abfahrt laut Fahrplan Minute (MM),
    ]
    print(ls)

def get_params(page_num):
    params = [
        {
            'S1F1': '01',       #Reisedatum Tag (TT)
            'S1F2': '01',       #Reisedatum Monat (MM)
            'S1F3': '24',       #Reisedatum Jahr (JJ)
            'S1F4': 'Test',     #Startbahnhof
            'S1F5': 'Test',     #Abfahrt laut Fahrplan Stunde (HH)
            'S1F6': 'Test',     #Abfahrt laut Fahrplan Minute (MM)
            'S1F7': 'Test',     #Zielbahnhof
            'S1F8': 'Test',     #Ankunftszeit laut Fahrplan Stunde (HH)
            'S1F9': 'Test',     #Ankunftszeit laut Fahrplan Minute (MM)
            'S1F10': 'Test',    #Ankunftsdatum Tag (TT)
            'S1F11': 'Test',    #Ankunftsdatum Monat (MM)
            'S1F12': 'Test',    #Ankunftsdatum Jahr (JJ)
            'S1F13': 'Test',    #Angekommen bin ich mit Zug Zugart (ICE/IC/RE/RB etc.)
            'S1F14': 'Test',    #Angekommen bin ich mit Zug Zugnummer
            'S1F15': 'Test',    #tatsächliche Ankunft Stunde (HH)
            'S1F16': 'Test',    #tatsächliche Ankunft Minute (MM)
            'S1F17': 'Test',    #Erster verspäteter/ausgefallener Zug Zugart (ICE/IC/RE/RB etc.)
            'S1F18': 'Test',    #Erster verspäteter/ausgefallener Zug Zugnummer
            'S1F19': 'Test',    #Erster verspäteter/ausgefallener Zug Abfahrt laut Fahrplan Stunde (HH)
            'S1F20': 'Test'     #Erster versp�teter/ausgefallener Zug � Abfahrt laut Fahrplan Minute (MM),
        },
        {
            'S2F4': 'Test'   #Name (Nachname)
        }
    ]
    return params[page_num]

def write_values():
    for page in pdf_reader.pages:
        page_num = pdf_reader.getPageNumber(page)
        pdf_writer.add_page(page)

        params = get_params(page_num)
        if page_num == 0: title = "-".join([params["S1F1"], params["S1F2"],params["S1F3"]])

        pdf_writer.update_page_form_field_values(
            pdf_writer.pages[page_num], params
        )

        with open(title + ".pdf", "wb") as output_stream:
            pdf_writer.write(output_stream)

##main
init()
#get_fields()   #Eingabefelder aus Dokument auslesen und in txt-Datei schreiben
#write_values()
read_table()