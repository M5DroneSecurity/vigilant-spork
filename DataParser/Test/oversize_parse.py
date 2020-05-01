"""
Title: oversize_parse.py
By: M5DS1
    Purpose:
        This function parses through this JSON file to extract the payload data for each packet.
        This payload data is then parsed using the MAVLINK 1.0 and 2.0 Serialization
        Outputs to Excel (.xlsx) Sheet in Results/ directory

        4/30/2020: modified to parse "Link Packets"
"""

import json
import pandas as pd
import numpy as np
import warnings

from plot_utils import *
from stat_utils import *

# warnings.filterwarnings("ignore")

''' Location of Data for Parsing '''
json_directory = '../Decrypted/Solo/solo_decrypted_json_20200223/'
# json_filename = 'solo_202002223_trial2_mavlink'
json_filename = 'solo_20200223_decrypted_json_trial1'
json_location = json_directory + json_filename + '.json'

''' Handle Oversized Packets '''
raw_link = []
oversize_data = []
ind_length = 0

''' Initialize Relevant Fields '''
frame_reltime = []
ip_src = []
ip_dst = []
udp_srcport = []
udp_dstport = []
data_len = []
data_data = []

''' Packet Count '''
v1_count = 0
v2_count = 0
dead = 0

''' Load JSON file '''
print("Grabbing JSON: ", json_location)
with open(json_location) as src_file:
    src_loader = json.load(src_file)

    ''' Parse through JSON file for specific information'''
    for packet in src_loader:
        try:
            packet_array = packet['_source']['layers']['data']['data.data'].split(':')
            ''' Filter for MavLink (1.0/2.0) and not RC packet'''
            if packet_array[0] in ['fe', 'fd'] and packet['_source']['layers']['udp']['udp.srcport'] != '5005':
                if packet_array[0] == 'fe':
                    v1_count += 1
                elif packet_array[0] == 'fd':
                    v2_count += 1

                ''' Start of overize packet parsing process '''
                if int(packet['_source']['layers']['data']['data.len']) > 56:
                    raw_link = packet['_source']['layers']['data']['data.data'].split(':')
                    oversize_data.append(raw_link[0:56])
                    del raw_link[0:56]

                    while len(raw_link) != 0:
                        if raw_link[0] == 'fe':
                            ind_length = int(raw_link[1], 16) + 8
                        elif raw_link[0] == 'fd':
                            ind_length = int(raw_link[1], 16) + 12
                        else:
                            print("incorrect link packet structure")
                            exit(-1)
                        oversize_data.append(raw_link[0:ind_length])
                        del raw_link[0:ind_length]

                    new_oversize = []
                    ''' rejoin oversize data into strings '''
                    for over in oversize_data:
                        new_oversize.append(':'.join(over))

                    ''' insert parsed oversized packets back into main lists '''
                    for ins in range(1,len(new_oversize)): ## ignore 56-byte header
                        frame_reltime.append(packet['_source']['layers']['frame']['frame.time_relative'])
                        ip_src.append(packet['_source']['layers']['ip']['ip.src'])
                        ip_dst.append(packet['_source']['layers']['ip']['ip.dst'])
                        udp_srcport.append(packet['_source']['layers']['udp']['udp.srcport'])
                        udp_dstport.append(packet['_source']['layers']['udp']['udp.dstport'])
                        data_len.append((len(new_oversize[ins]) + 1) / 3)
                        data_data.append(new_oversize[ins])

                    ''' clear temp list '''
                    oversize_data.clear()

                else:
                    ''' typical parsing process '''
                    ip_src.append(packet['_source']['layers']['ip']['ip.src'])
                    ip_dst.append(packet['_source']['layers']['ip']['ip.dst'])
                    udp_srcport.append(packet['_source']['layers']['udp']['udp.srcport'])
                    udp_dstport.append(packet['_source']['layers']['udp']['udp.dstport'])
                    frame_reltime.append(packet['_source']['layers']['frame']['frame.time_relative'])
                    data_len.append(packet['_source']['layers']['data']['data.len'])
                    data_data.append(packet['_source']['layers']['data']['data.data'])
            else:
                dead += 1
        except KeyError:
            # print("Failed to append Data, KeyError. Packet " + str(count))
            dead += 1

    ''' Output Count Statistics to Console '''
    print("Non-MavLink Packets: ", dead)
    print("Mavlink 2.0 Packets: ", v2_count)
    print("Mavlink 1.0 Packets: ", v1_count)

''' Create a 2D Array that contains shows packets by split byte-fields '''
split_data = []
for dat in range(len(data_data)):
    split_data.append(data_data[dat].split(':'))
    # print(split_data[dat])

# print("DEBUG: Length of split_data is {}".format(split_data))
print("Total MavLink Packets: {}".format(len(data_data)))

'''
First, lets split these data into MavLink fields.. 
v1.0 uses [0][1][2][3][4][5][6:-2][-2:]
v2.0 uses [0][1][2][3][4][5][6][7:10][10:-3][-2:]

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
payload_length = []

''' Store data in these field arrays '''
for n in range(len(data_data)):
    # print(data_data[n])
    payload_length.append(len(split_data[n][6:-2]))
    magic.append(split_data[n][0])
    length.append(split_data[n][1])
    if len(split_data[n]) == 56:
        print("huge", split_data[n])


    elif split_data[n][0] == 'fe':
        try:
            incompat_flags.append("--")
            compat_flags.append("--")
            seq.append(split_data[n][2])
            sysid.append(split_data[n][3])
            compid.append(split_data[n][4])
            msgid.append(split_data[n][5])
            payload.append(' '.join(split_data[n][6:-2]))
            checksum.append(' '.join(split_data[n][-2:]))
        except IndexError:
            print("IndexError: fix immediately", split_data[n])

    elif split_data[n][0] == 'fd':
        try:
            incompat_flags.append(split_data[n][2])
            compat_flags.append(split_data[n][3])
            seq.append(split_data[n][4])
            sysid.append(split_data[n][5])
            compid.append(split_data[n][6])
            msgid.append(' '.join(split_data[n][7:10]))
            payload.append(' '.join(split_data[n][10:-2]))
            checksum.append(' '.join(split_data[n][-2:]))
        except IndexError:
            print("IndexError: fix immediately", split_data[n])

''' DEBUG '''
print("{}\n{}\n{}\n{}\n{}\n".format(len(ip_src), len(ip_dst), len(frame_reltime), len(data_len), len(data_data)))
print("magic={} len={} inc={} com={} seq={} sys={} cid={} msg={} pay={} chk={}".format(len(magic), len(length),
                                            len(incompat_flags), len(compat_flags), len(seq), len(sysid), len(compid),
                                            len(msgid), len(payload), len(checksum)))

''' Provide Message Definitions '''
message_name = []
occur_name = []
occur_def = []
occur = fieldcounter(msgid)

for m in msgid:
    message_name.append(message_decoder(str(m), '../Includes/v1.0/', 'n'))
for m in list(occur.keys()):
    occur_name.append(message_decoder(str(m), '../Includes/v1.0/', 'n'))
    occur_def.append(message_decoder(str(m), '../Includes/v1.0/', 'd'))


''' Generate Dataframe for All Packets '''
clean = pd.DataFrame(np.column_stack([magic, length, incompat_flags, compat_flags, seq, sysid, compid, msgid,
                                      payload, checksum, payload_length, ip_src, ip_dst, frame_reltime, message_name]),
                     columns=['magic', 'length', 'incompat_flags', 'compat_flags', 'seq', 'sysid', 'compid', 'msgid',
                              'payload', 'checksum ', 'PAYLOAD_LENGTH', 'IP_SRC', 'IP_DST', 'FRAME_RELTIME', 'MESSAGE'])

''' Convert some fields to numeric '''
clean['PAYLOAD_LENGTH'] = pd.to_numeric(clean['PAYLOAD_LENGTH'])
clean['FRAME_RELTIME'] = pd.to_numeric(clean['FRAME_RELTIME'])

''' Generate Dataframe for Message IDs '''
msg_ids = pd.DataFrame(np.column_stack([list(fieldcounter(msgid).keys()), list(fieldcounter(msgid).values()),
                                        occur_name, occur_def]),
                       columns=['Msg_ID', 'Occurrences', 'Name', 'Definition'])

''' Sort occurrence count from most to least frequent '''
msg_ids['Occurrences'] = pd.to_numeric(msg_ids['Occurrences'])
msg_ids.sort_values(['Occurrences'], ascending=False, inplace=True)
# print("DEBUG: msg_id count: " + msg_ids)

'''
Let's display parsed data and occurance count in an excel file (.xlsx)
NOTE: I can't autofit columns through the script but here's how to do it manually:
https://support.office.com/en-us/article/change-the-column-width-and-row-height-72f5e3cc-994d-43e8-ae58-9774a0905f46
'''
with pd.ExcelWriter('../Results/' + json_filename + '.xlsx', engine='xlsxwriter') as writer:
    ''' Bulk Data '''
    clean.to_excel(writer, sheet_name='All Packets')
    msg_ids.to_excel(writer, sheet_name='Occurrences')
    occur_grapher(writer, 'Occurrences', msg_ids)

    ''' Msg_IDs '''
    for msg in list(msg_ids['Msg_ID']):
        data = clean.loc[clean['msgid'] == msg]
        del data['MESSAGE']
        data['TIME_DELTA'] = data['FRAME_RELTIME'] - data['FRAME_RELTIME'].shift(1)
        data.to_excel(writer, sheet_name='msgID-' + msg)
        payload_grapher(writer, 'msgID-' + msg, data, msg)
        time_grapher(writer, 'msgID-' + msg, data, msg)
        stat_tabler(writer, 'msgID-' + msg, data, msg)

print("Finished!! Outputted to:  " + '../Results/' + json_filename + '.xlsx')
print('\n')
