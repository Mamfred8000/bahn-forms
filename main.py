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
## write dict to txt-file
    for key, value in d.items():
        txt_writer.write('\t' * indent + str(key) + '\n')
        if isinstance(value, dict):
            write_dict(value, indent+1)
        else:
            txt_writer.write('\t' * (indent+1) + str(value) + '\n')

def get_fields():
## read fields of formula from pdf
    global txt_file
    global txt_writer
    txt_file = "fields.txt"
    fields_dict = pdf_reader.get_fields()
    with open(txt_file, "w+") as txt_writer:
        write_dict(fields_dict)

def read_table():
## read excel-table with train delays
    dtype_dict = {
        'Datum' : 'str',
        'Status' : 'str',
        ## fix! Cant read the column
        #'Abgebrochen' : 'str',
        'Start' : 'str',
        'Ziel' : 'str',
        'Zug Plan' : 'str',
        'Abfahrt Plan' : 'str',
        'Ankunft Plan' : 'str',
        'Zug Tats'  : 'str',
        'Ankunft Tats' : 'str'
    }
    usecols = list(dtype_dict.keys())
    df = pd.read_excel(delay_table, usecols=usecols, dtype=dtype_dict)
    df = df.loc[df['Status'] == 'test']

    ## hier weiter machen und alle Spalten definieren!
    df_values = pd.DataFrame()
    df_values["Reisedatum Tag (TT)"] = df['Datum'].str[8:10]
    df_values["Reisedatum Monat (MM)"] = df['Datum'].str[5:7]
    df_values["Reisedatum Jahr (JJ)"] = df['Datum'].str[2:4]
    df_values["Startbahnhof"] = df['Start']
    df_values["Abfahrt laut Fahrplan Stunde (HH)"] = df["Abfahrt Plan"].str[0:2]
    df_values["Abfahrt laut Fahrplan Stunde (MM)"] = df["Abfahrt Plan"].str[3:5]
    df_values["Zielbahnhof"] = df['Ziel']

    ## brauche ich eigentlich nicht mehr, nur noch für Beschreibungen
    ls = [
            df['Datum'],    #Reisedatum Tag (TT)
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
    #print(df_values)
    return(df_values)

def get_params(page_num, table_item):
    params = [
        {
            'S1F1': table_item["Reisedatum Tag (TT)"],
            'S1F2': table_item["Reisedatum Monat (MM)"],
            'S1F3': table_item["Reisedatum Jahr (JJ)"],
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
    delay_table = read_table()
    ## iterate over the rows of the delay excel table
    for _index, row in delay_table.iterrows():
        ## iterate over pages of the pdf formular
        for page in pdf_reader.pages:
            page_num = pdf_reader.getPageNumber(page)
            pdf_writer.add_page(page)

            ## pass the values of the delay table in the right format for the formular
            params = get_params(page_num, row)

            ## define file name from date of delay item
            if page_num == 0: title = "-".join([params["S1F1"], params["S1F2"],params["S1F3"]])

            ## write
            pdf_writer.update_page_form_field_values(
                pdf_writer.pages[page_num], params
            )
            with open(title + ".pdf", "wb") as output_stream:
                pdf_writer.write(output_stream)

def test_function():
    delay_table = read_table()
    for index, row in delay_table.iterrows():
        for page in pdf_reader.pages:
            page_num = pdf_reader.getPageNumber(page)
            pdf_writer.add_page(page)

            params = get_params(page_num, row)
            print(params)

#main
init()
write_values()

##zum Parameter auslesen
#read_table()
#get_fields()