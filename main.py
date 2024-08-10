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
        'Abgebrochen' : 'str',
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
    df = df.loc[df['Status'] == 'offen']

    df_values = pd.DataFrame()
    df_values["Reisedatum Tag (TT)"] = df['Datum'].str[8:10]
    df_values["Reisedatum Monat (MM)"] = df['Datum'].str[5:7]
    df_values["Reisedatum Jahr (JJ)"] = df['Datum'].str[2:4]
    df_values["Startbahnhof"] = df['Start']
    df_values["Abfahrt laut Fahrplan Stunde (HH)"] = df["Abfahrt Plan"].str[0:2]
    df_values["Abfahrt laut Fahrplan Minute (MM)"] = df["Abfahrt Plan"].str[3:5]
    df_values["Zielbahnhof"] = df['Ziel']
    df_values["Ankunftszeit laut Fahrplan Stunde (HH)"] = df["Ankunft Plan"].str[0:2]
    df_values["Ankunftszeit laut Fahrplan Minute (MM)"] = df["Ankunft Plan"].str[3:5]
    df_values["Ankunftsdatum Tag (TT)"] = df['Datum'].str[8:10]
    df_values["Ankunftsdatum Monat (MM)"] = df['Datum'].str[5:7]
    df_values["Ankunftsdatum Jahr (JJ)"] = df['Datum'].str[2:4]
    df_values["Angekommen bin ich mit Zug Zugart (ICE/IC/RE/RB etc.)"] = df['Zug Tats'].str.split().str[0]
    df_values["Angekommen bin ich mit Zug Zugnummer"] = df['Zug Tats'].str.split().str[1]
    df_values["tatsächliche Ankunft Stunde (HH)"] = df["Ankunft Tats"].str[0:2]
    df_values["tatsächliche Ankunft Minute (MM)"] = df["Ankunft Tats"].str[3:5]
    df_values["Erster verspäteter/ausgefallener Zug Zugart (ICE/IC/RE/RB etc.)"] = df['Zug Plan'].str.split().str[0]
    df_values["Erster verspäteter/ausgefallener Zug Zugnummer"] = df['Zug Plan'].str.split().str[1]
    df_values["Erster verspäteter/ausgefallener Zug Abfahrt laut Fahrplan Stunde (HH)"] = df["Abfahrt Plan"].str[0:2]
    df_values["Erster verspäteter/ausgefallener Zug Abfahrt laut Fahrplan Minute (MM)"] = df["Abfahrt Plan"].str[3:5]
    df_values["Abgebrochen"] = df["Abgebrochen"]

    return(df_values)

def get_params(page_num, table_item):
    params = [
        {
            'S1F1': table_item["Reisedatum Tag (TT)"],
            'S1F2': table_item["Reisedatum Monat (MM)"],
            'S1F3': table_item["Reisedatum Jahr (JJ)"],
            'S1F4': table_item["Startbahnhof"],
            'S1F5': table_item["Abfahrt laut Fahrplan Stunde (HH)"],
            'S1F6': table_item["Abfahrt laut Fahrplan Minute (MM)"],
            'S1F7': table_item["Zielbahnhof"],
            'S1F8': table_item["Ankunftszeit laut Fahrplan Stunde (HH)"],
            'S1F9': table_item["Ankunftszeit laut Fahrplan Minute (MM)"],
            'S1F10': table_item["Ankunftsdatum Tag (TT)"],
            'S1F11': table_item["Ankunftsdatum Monat (MM)"],
            'S1F12': table_item["Ankunftsdatum Jahr (JJ)"],
            'S1F13': table_item["Angekommen bin ich mit Zug Zugart (ICE/IC/RE/RB etc.)"],
            'S1F14': table_item["Angekommen bin ich mit Zug Zugnummer"],
            'S1F15': table_item["tatsächliche Ankunft Stunde (HH)"],
            'S1F16': table_item["tatsächliche Ankunft Minute (MM)"],
            'S1F17': table_item["Erster verspäteter/ausgefallener Zug Zugart (ICE/IC/RE/RB etc.)"],
            'S1F18': table_item["Erster verspäteter/ausgefallener Zug Zugnummer"],
            'S1F19': table_item["Erster verspäteter/ausgefallener Zug Abfahrt laut Fahrplan Stunde (HH)"],
            'S1F20': table_item["Erster verspäteter/ausgefallener Zug Abfahrt laut Fahrplan Minute (MM)"],
            'S1F25': "/Ja"
        },
        {
            #Direkt in Vorlage PDF ausgefüllt
            #'S2F4': 'Test'   #Name (Nachname)
        }
    ]
    if table_item["Abgebrochen"] == "x":
        params[0]["S1F10"] = ""
        params[0]["S1F11"] = ""
        params[0]["S1F12"] = ""
        params[0]["S1F13"] = ""
        params[0]["S1F14"] = ""
        params[0]["S1F15"] = ""
        params[0]["S1F16"] = ""
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
            if page_num == 0: title = "-".join([params["S1F1"], params["S1F2"],params["S1F3"],params["S1F17"],params["S1F18"]])

            ## write
            pdf_writer.update_page_form_field_values(
                pdf_writer.pages[page_num], params
            )
            with open(title + ".pdf", "wb") as output_stream:
                pdf_writer.write(output_stream)
    print("saved", len(delay_table), "files")


#main
init()
write_values()

###zum Parameter auslesen
#get_fields()