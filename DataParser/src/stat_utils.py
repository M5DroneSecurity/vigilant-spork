"""
Title: stat_utils.py
By: M5DS1
Description:
    Contains functions for the yellow stat table, etc.
"""

import xml.etree.ElementTree as ET
import os

'''
Function that parses through each field and returns an occurance count of data within each field
@input: 
@output: 
'''


def fieldcounter(data_field):
    count_arr = {}
    for d in data_field:
        if d in count_arr:
            count_arr[d] += 1
        else:
            count_arr[d] = 1

    return count_arr


# print(list(fieldcounter(msgid).keys()))


'''
Function that compares the msgid to the common_messages.xml to find the msg_type
Function that compares the msgid to all dialects of v1.0 messages to find the msg definition
@input: msg_id
@output: msg_type
'''


def message_decoder(msgid, def_dir, mode):
    '''grab msgid as str'''
    m = msgid.replace(" ", "")

    ''' str -> hex -> int -> str '''
    m = bytearray.fromhex(m)
    m.reverse()
    m = int.from_bytes(m, byteorder='big', signed=False)
    m = str(m).lstrip()

    ''' Compare to XML '''
    for definition in os.listdir(def_dir):
        xml_path = def_dir+definition
        if definition.endswith(".xml"):
            xml_file = ET.parse(def_dir + definition)
            xml_message = xml_file.findall('messages/message')
            for mes in xml_message:
                xml_id = mes.attrib['id']
                xml_name = mes.attrib['name']
                try:
                    xml_desc = mes.find('description').text
                except:
                    xml_desc = "description not found"
                if xml_id == m:
                    if mode == "n":
                        return xml_name
                    elif mode == "d":
                        print(
                            "statutils.py | Grabbing XML from {}\nFound {} [msgid-{}]: \n{}\n".format(xml_path, xml_name,
                                                                                                    xml_id, xml_desc))
                        return xml_desc

    return "--"


'''
Function that creates a stat table w/ msg_type, count, ave_delta, delta_stddev, ave_plen
@input: writer, sheet,
@output: array with top 5 msgids as strings
'''


def stat_tabler(writer_, sheet_, data_, msg_):
    workbook = writer_.book
    worksheet = writer_.sheets[sheet_]
    cell_format = workbook.add_format({'bold': True, 'bg_color': 'yellow'})
    cell_format2 = workbook.add_format({'bg_color': 'yellow'})

    pList = list(data_['PAYLOAD_LENGTH'])
    r1 = 2
    r2 = len(pList) + 1

    worksheet.write('S2', 'Msg Name:', cell_format)
    worksheet.write('T2', message_decoder(msg_, './Includes/v1.0/', 'n'), cell_format2)

    worksheet.write('S3', 'Msg Definition:', cell_format)
    worksheet.write('T3', message_decoder(msg_, './Includes/v1.0/', 'd'), cell_format2)

    worksheet.write('S4', 'Count:', cell_format)
    worksheet.write_formula('T4', '=COUNTA(B{0}:B{1})'.format(r1, r2), cell_format2)

    worksheet.write('S5', 'Ave Delta:', cell_format)
    worksheet.write_formula('T5', '=AVERAGE(P{0}:P{1})'.format(r1, r2), cell_format2)

    worksheet.write('S6', 'Delta Std Dev:', cell_format)
    worksheet.write_formula('T6', '=STDEV(P{0}:P{1})'.format(r1, r2), cell_format2)

    worksheet.write('S7', 'Ave Payload Length:', cell_format)
    worksheet.write_formula('T7', '=AVERAGE(L{0}:L{1})'.format(r1, r2), cell_format2)
