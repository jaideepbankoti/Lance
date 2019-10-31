import socket
import os
import sys
import subprocess
import time
import struct
from termcolor import colored
import codecs
import csv
import shutil
from tempfile import NamedTemporaryFile


FIELDS = ['File', 'User_ID', 'Action', 'IP', 'Timestamp']

def add_user(uname, uid):
    list = [uname,uid]
    with codecs.open('beta/userlist.csv','a','utf-8') as csvfile:
        linewriter = csv.writer(csvfile,delimiter = ',',quotechar = '\"')
        linewriter.writerow(list)

def del_user(uname,uid):
    list = [uname,uid]
    tempfile = NamedTemporaryFile(mode='w', delete=False)
    with codecs.open('beta/userlist.csv','r','utf-8') as csvfile,tempfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='\"')
        writer = csv.writer(tempfile, delimiter=',', lineterminator='\n', quotechar='\"')
        for row in reader:
            if row == list:
                pass
            else:
                writer.writerow(row)
    shutil.move(tempfile.name, 'beta/userlist.csv')

def welcome_msg():
    return 'Welcome to our chatroom! We are the beta and we always stay at the top.'

def list_of_files(conn, uid):
    print('Listing files to {}...'.format(uid))
    listing = os.listdir(os.getcwd()+'/beta/files')
    conn.send(struct.pack("i", len(listing)))
    total_directory_size = 0
    for i in listing:
        conn.send(str.encode(i+':'+str(os.path.getsize(os.getcwd()+'/beta/files/'+i))))
        total_directory_size += os.path.getsize(os.getcwd()+'/beta/files/'+i)
        conn.recv(1024)
    conn.send(struct.pack("i", total_directory_size))
    conn.recv(1024)
    print('Successfully sent file listing')
    return

def upload_file(conn, address, uid):
    conn.send(str.encode('1'))
    file_name_size = struct.unpack("h", conn.recv(2))[0]
    file_name = str(conn.recv(file_name_size),'utf-8').split('/')[-1]
    conn.send(str.encode('1'))
    file_size = struct.unpack("i", conn.recv(4))[0]
    start_time = time.time()
    output_file = open('beta/files/'+file_name, "wb")
    bytes_recieved = 0
    print('\nRecieving from {}...'.format(uid))
    while bytes_recieved < file_size:
        l = conn.recv(1024)
        output_file.write(l)
        bytes_recieved += 1024
    output_file.close()
    print('\nRecieved file: {}'.format(file_name))
    conn.send(struct.pack("f", time.time() - start_time))
    conn.send(struct.pack("i", file_size))
    ip, port = address
    row = dict()
    row = {FIELDS[0]: file_name, FIELDS[1]: uid, FIELDS[2]: 'Upload', FIELDS[3]: ip,
           FIELDS[4]: str(time.ctime(time.time()))}
    with codecs.open('beta/log.csv','a','utf-8') as csvfile:
        linewriter = csv.DictWriter(csvfile, FIELDS, delimiter='\t' )
        linewriter.writerow(row)
    return

def download_file(conn, address, uid):
    conn.send(str.encode('1'))
    file_name_length = struct.unpack("h", conn.recv(2))[0]
    file_name = conn.recv(file_name_length)
    file_name = str(file_name,'utf-8')
    print(file_name)
    if os.path.isfile(os.getcwd()+'/beta/files/'+file_name):
        conn.send(struct.pack("i", os.path.getsize(os.getcwd()+'/beta/files/'+file_name)))
    else:
        print('File name not valid')
        conn.send(struct.pack("i", -1))
        return
    conn.recv(1024)
    start_time = time.time()
    print('Sending file to {}...'.format(uid))
    content = open('beta/files/'+file_name, "rb")
    l = content.read(1024)
    while l:
        conn.send(l)
        l = content.read(1024)
    content.close()
    conn.recv(1024)
    conn.send(struct.pack("f", time.time() - start_time))
    ip, port = address
    row = dict()
    row = {FIELDS[0]: file_name, FIELDS[1]: uid, FIELDS[2]: 'Download', FIELDS[3]: ip,
           FIELDS[4]: str(time.ctime(time.time()))}
    with codecs.open('beta/log.csv','a','utf-8') as csvfile:
        linewriter = csv.DictWriter(csvfile, FIELDS, delimiter='\t' )
        linewriter.writerow(row)
    return

def del_file(conn, address, uid):
    conn.send(str.encode('1'))
    file_name_length = struct.unpack("h", conn.recv(2))[0]
    file_name = conn.recv(file_name_length)
    file_name = str(file_name,'utf-8')
    print(file_name)
    if os.path.isfile(os.getcwd()+'/beta/files/'+file_name):
        conn.send(struct.pack("i", 1))
    else:
        conn.send(struct.pack("i", -1))
    confirm_delete = conn.recv(1024)
    confirm_delete = str(confirm_delete,'utf-8')
    if confirm_delete == "Y":
        try:
            os.remove(os.getcwd()+'/beta/files/'+file_name)
            print('Deleted file {} by {}...'.format(file_name,uid))
            conn.send(struct.pack("i", 1))
        except:
            print('Failed to delete {}'.format(file_name))
            conn.send(struct.pack("i", -1))
    else:
        print('Delete abandoned by client!')
    ip, port = address
    row = dict()
    row = {FIELDS[0]: file_name, FIELDS[1]: uid, FIELDS[2]: 'Delete', FIELDS[3]: ip,
           FIELDS[4]: str(time.ctime(time.time()))}
    with codecs.open('beta/log.csv', 'a', 'utf-8') as csvfile:
        linewriter = csv.DictWriter(csvfile, FIELDS, delimiter='\t')
        linewriter.writerow(row)
    return

def show_logs(conn, uid):
    print('Showing logs to {}...'.format(uid))
    msg = []
    with codecs.open('beta/log.csv','rb','utf-8') as csvfile:
        linereader = csv.reader(csvfile, delimiter = '>', quotechar = '\"')
        for row in linereader:
            msg.append('\t'.join(row))
    conn.send(str.encode('\n'.join(msg)))

def msgs(conn, uid):
    csvfile = codecs.open('beta/msglog.csv', 'rb', 'utf-8')
    linereader = csv.reader(csvfile, delimiter='\t', quotechar='\"')
    while True:
        msg = []
        for row in linereader:
            msg.append('>'.join(row))
        conn.send(str.encode('\n'.join(msg)))
        msg = conn.recv(2048)
        msg = str(msg, 'utf-8')
        if msg != 'quit':
            msg = [uid, time.ctime(time.time()), msg]
            print('Recieved message: '+ '>'.join(msg))
            with codecs.open('beta/msglog.csv','a','utf-8') as csvfile:
                linewriter = csv.writer(csvfile, delimiter = '>', quotechar = '\"')
                linewriter.writerow(msg)
        else:
            print(uid+ ' left message chat!')
            break
    return

def quit_rm(conn,uid):
    print('{} quit the room...'.format(uid))
    return