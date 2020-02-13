"""
Title: data_parser.py
By: M5DS1
    Purpose:
        This function parses through this JSON file to extract the payload data for each packet.
        This payload data is then parsed using the MAVLINK 2.0 Serialization
        Outputs to Excel (.xlsx) Sheet in Results/ directory
"""

import json
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

""" For Pycharm """
from plot_utils import *
from stat_utils import *

""" For Anaconda Prompt """
# from src.plot_utils import *
# from src.stat_utils import *


def data_parser(json_directory, json_filename):
    ''' Location of Data for Parsing '''
    json_location = json_directory + json_filename + '.json'

    ''' Initialize Relevant Fields '''
    ip_src = []
    ip_dst = []
    frame_reltime = []
    payload_len = []
    data_len = []
    data_data = []
    count = 0
    dead = 0

    ''' MAVLINK 1.0 Parser '''
    old_count = 0
    old_ip_src = []
    old_ip_dst = []
    old_frame_reltime = []
    old_payload_len = []
    old_data_len = []
    old_data_data = []

    ''' Load JSON file '''
    print("Grabbing JSON: ", json_location)
    with open(json_location) as src_file:
        src_loader = json.load(src_file)

        ''' Parse through JSON file for specific information'''
        for packet in src_loader:
            try:
                packet_array = packet['_source']['layers']['data']['data.data'].split(':')
                ''' Filter for MavLink 2.0 '''
                if packet_array[0] == 'fe':
                    ''' Relevant fields '''
                    ip_src.append(packet['_source']['layers']['ip']['ip.src'])
                    ip_dst.append(packet['_source']['layers']['ip']['ip.dst'])
                    frame_reltime.append(packet['_source']['layers']['frame']['frame.time_relative'])
                    payload_len.append(int(packet['_source']['layers']['data']['data.len']) - 12)
                    data_len.append(packet['_source']['layers']['data']['data.len'])
                    data_data.append(packet['_source']['layers']['data']['data.data'])
                    count += 1
                # elif packet_array[0] == 'fe':
                #     old_count += 1
                else:
                    dead += 1
            except KeyError:
                # print("Failed to append Data, KeyError. Packet " + str(count))
                count += 1
                dead += 1
        print("Non-MavLink Packets: ", dead)
        print("Mavlink 2.0 Packets: ", count)
        print("Mavlink 1.0 Packets: ", old_count)
        # for n in range(len(src_loader)):
        #     print("DEBUG src_loader:  {}\t{}".format(data_len[n], data_data[n]))

    ''' Create a 2D Array that contains shows packets by split byte-fields '''
    split_data = []
    for dat in range(len(data_data)):
        split_data.append(data_data[dat].split(':'))
        # print(split_data[dat])

    # print("DEBUG: Length of split_data is {}".format(split_data))
    print("MavLink Packets: {}".format(len(data_data)))


    '''
    First, lets split these data into MavLink fields.. [0][1][2][3][4][5][6][7:10][10:-3][-3:]
    
    Serialization format: https://mavlink.io/en/guide/serialization.html
    '''

    ''' Declare arrays for each field '''
    magic = []
    length = []
    incompat_flags = []
    compat_flags = []
    seq = []
    sysid = []
    compid = []
    msgid = []
    payload = []
    checksum = []

    ''' Store data in these field arrays '''
    for n in range(len(data_data)):
        magic.append(split_data[n][0])
        length.append(split_data[n][1])
        incompat_flags.append(split_data[n][2])
        compat_flags.append(split_data[n][3])
        seq.append(split_data[n][4])
        sysid.append(split_data[n][5])
        compid.append(split_data[n][6])
        msgid.append(' '.join(split_data[n][7:10]))
        payload.append(' '.join(split_data[n][10:-2]))
        checksum.append(' '.join(split_data[n][-2:]))

    clean = pd.DataFrame(np.column_stack([magic, length, incompat_flags, compat_flags, seq, sysid, compid, msgid, payload,
                                          checksum, payload_len, ip_src, ip_dst, frame_reltime]),
                         columns=['magic [0]', 'length [1]', 'incompat_flags [2]', 'compat_flags [3]', 'seq [4]',
                                  'sysid [5]', 'compid [6]', 'msgid [7:10]', 'payload [10:-2]', 'checksum [-2:]',
                                  'PAYLOAD_LENGTH', 'IP_SRC', 'IP_DST', 'FRAME_RELTIME'])

    ''' Convert some fields to numeric '''
    clean['FRAME_RELTIME'] = pd.to_numeric(clean['FRAME_RELTIME'])
    clean['PAYLOAD_LENGTH'] = pd.to_numeric(clean['PAYLOAD_LENGTH'])

    ''' creates dataframe for occurrence count of each field '''
    # occurrences = pd.DataFrame(np.column_stack([fieldcounter(magic), fieldcounter(length), fieldcounter(incompat_flags),
    #                                            fieldcounter(compat_flags), fieldcounter(sysid),
    #                                            fieldcounter(compid), fieldcounter(msgid)]),
    #                           columns=['magic [0]', 'length [1]', 'incompat_flags [2]', 'compat_flags [3]', 'sysid [5]',
    #                                    'compid [6]', 'msgid [7:10]'])

    ''' create dataframe for occurrence count of msg_ids '''
    msg_ids = pd.DataFrame(np.column_stack([list(fieldcounter(msgid).keys()), list(fieldcounter(msgid).values())]),
                              columns=['Msg_ID', 'Occurrences'])

    ''' Sort occurrence count from greatest to least frequent '''
    msg_ids['Occurrences'] = pd.to_numeric(msg_ids['Occurrences'])
    msg_ids.sort_values(['Occurrences'], ascending=False, inplace=True)
    # print("DEBUG: msg_id count: " + msg_ids)

    '''
    Let's display parsed data and occurance count in an excel file (.xlsx)
    NOTE: I can't autofit columns through the script but here's how to do it manually:
    https://support.office.com/en-us/article/change-the-column-width-and-row-height-72f5e3cc-994d-43e8-ae58-9774a0905f46
    '''
    with pd.ExcelWriter('Results/'+json_filename+'.xlsx', engine='xlsxwriter') as writer:
        ''' Bulk Data '''
        clean.to_excel(writer, sheet_name='All Packets')
        msg_ids.to_excel(writer, sheet_name='Occurrences')
        occur_grapher(writer, 'Occurrences', msg_ids)

        ''' Heartbeat '''
        hb = clean.loc[clean['msgid [7:10]'] == '00 00 00']
        hb['TIME_DELTA'] = hb['FRAME_RELTIME'] - hb['FRAME_RELTIME'].shift(1)
        hb.to_excel(writer, sheet_name='msgID-'+'00 00 00')
        payload_grapher(writer, 'msgID-00 00 00', hb, '00 00 00')
        time_grapher(writer, 'msgID-00 00 00', hb, '00 00 00')
        # density_grapher(writer, 'msgID-00 00 00', hb, '00 00 00')
        stat_tabler(writer, 'msgID-00 00 00', hb, '00 00 00')

        ''' Top 4 Msg_IDS '''
        for msg in list(msg_ids['Msg_ID'])[0:4]:
            data = clean.loc[clean['msgid [7:10]'] == msg]
            data['TIME_DELTA'] = data['FRAME_RELTIME'] - data['FRAME_RELTIME'].shift(1)
            data.to_excel(writer, sheet_name='msgID-'+msg)
            payload_grapher(writer, 'msgID-'+msg, data, msg)
            time_grapher(writer, 'msgID-'+msg, data, msg)
            # density_grapher(writer,'msgID-'+msg, data, msg)
            stat_tabler(writer, 'msgID-'+msg, data, msg)

    print("Finished!! Outputted to:  " + 'Results/' + json_filename + '.xlsx \n')
