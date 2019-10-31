"""
Dependenies required:-
    termcolor
References:-
    FTP file server via socket programming in Python - https://github.com/E-Renshaw/ftp-socket-server-python
    Creating shell and threads(server and client) -  https://www.youtube.com/playlist?list=PLhTjy8cBISErYuLZUvVOYsR1giva2payF
    Working with CSV file - https://www.geeksforgeeks.org/working-csv-files-python/
    Updating rows in CSV file - https://stackoverflow.com/questions/46126082/how-to-update-rows-in-a-csv-file
    Coloring text in python - https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-terminal-in-python
"""



import threading
import socket
import os
import sys
import time
from tempfile import NamedTemporaryFile
import shutil
import csv
import struct
import codecs
from queue import Queue
from alpha import alpha
from beta import beta
from gamma import gamma
from omega import omega
from zeta import zeta

NUMBER_OF_THREADS = 4
JOB_NUMBER = [1,2,3,4]
queue = Queue()
GROUPS = []

with codecs.open("Groups.csv", 'r', 'utf-8') as csvfile:
    linereader = csv.reader(csvfile, delimiter=',', quotechar='\"')
    for row in linereader:
        GROUPS.extend(row)      #contains the number of groups as an iterable
#create a Socket (connect two computers)
def create_socket():
    try:
        global host
        global command_port
        global data_port
        global cs
        global ds
        host = ""
        command_port = 9999
        data_port = 8488
        cs = socket.socket()
        ds = socket.socket()

    except socket.error as msg:
        print("Socket creation error: " + str(msg))

# binding the sockets and listening for connections
def bind_socket():
    try:
        global host
        global command_port
        global data_port
        global cs
        global ds

        print("Binding the Port " + str(command_port) +" "+ str(data_port))

        cs.bind((host,command_port))
        cs.listen(5)
        ds.bind((host, data_port))
        ds.listen(5)

    except socket.error as msg:
        print('Socket Binding error'+ str(msg)+"\n"+"Retrying...")
        bind_socket()

def accept_command_connection():

    while True:
        try:
            cs_conn, cs_address = cs.accept()
            cs.setblocking(1) #prevents timeout

            print('\nCommand Connection has been established :' + cs_address[0])
            th = threading.Thread(target=recieve_command, args=(cs_conn, cs_address))
            th.daemon = True
            th.start()
        except:
            pass

def accept_data_connection():

    while True:
        try:
            ds_conn, ds_address = ds.accept()
            ds.setblocking(1)  # prevents timeout
            print('\nData Connection has been established :' + ds_address[0])
            th = threading.Thread(target=recieve_data, args=(ds_conn, ds_address))
            th.daemon = True
            th.start()
        except:
            pass

def list_files(conn, uid, group_in):
    if group_in == 'alpha':
        alpha.list_of_files(conn, uid)
    if group_in == 'beta':
        beta.list_of_files(conn, uid)
    if group_in == 'gamma':
        gamma.list_of_files(conn, uid)
    if group_in == 'omega':
        omega.list_of_files(conn, uid)
    if group_in == 'zeta':
        zeta.list_of_files(conn, uid)

def upload(conn,address, uid, group_in):
    if group_in == 'alpha':
        alpha.upload_file(conn, address, uid)
    if group_in == 'beta':
        beta.upload_file(conn, address, uid)
    if group_in == 'gamma':
        gamma.upload_file(conn, address, uid)
    if group_in == 'omega':
        omega.upload_file(conn, address, uid)
    if group_in == 'zeta':
        zeta.upload_file(conn, address, uid)

def download(conn,address, uid, group_in):
    if group_in == 'alpha':
        alpha.download_file(conn,address,uid)
    if group_in == 'beta':
        beta.download_file(conn,address,uid)
    if group_in == 'gamma':
        gamma.download_file(conn,address,uid)
    if group_in == 'omega':
        omega.download_file(conn,address,uid)
    if group_in == 'zeta':
        zeta.download_file(conn,address,uid)

def delete_file(conn,address, uid, group_in):
    if group_in == 'alpha':
        alpha.del_file(conn,address,uid)
    if group_in == 'beta':
        beta.del_file(conn,address,uid)
    if group_in == 'gamma':
        gamma.del_file(conn,address,uid)
    if group_in == 'omega':
        omega.del_file(conn,address,uid)
    if group_in == 'zeta':
        zeta.del_file(conn,address,uid)

def share_file(conn,address, uid, group_in, g_name ):
    with codecs.open("data_file.csv", "r", 'utf-8') as csvfile:
        linereader = csv.reader(csvfile, delimiter=',', quotechar="\"")
        for row in linereader:
            if row[1] == uid:
                if g_name not in row:
                    conn.send(str.encode('0'))
                    return
    conn.send(str.encode('1'))
    print("{} is sharing file...".format(uid))
    pass                                                        #to complete

def show_log(conn, uid, group_in):
    if group_in == 'alpha':
        alpha.show_logs(conn,uid)
    if group_in == 'beta':
        beta.show_logs(conn,uid)
    if group_in == 'gamma':
        gamma.show_logs(conn,uid)
    if group_in == 'omega':
        omega.show_logs(conn,uid)
    if group_in == 'zeta':
        zeta.show_logs(conn,uid)

def messages(conn, uid, group_in):
    if group_in == 'alpha':
        alpha.msgs(conn, uid)
    if group_in == 'beta':
        beta.msgs(conn, uid)
    if group_in == 'gamma':
        gamma.msgs(conn, uid)
    if group_in == 'omega':
        omega.msgs(conn, uid)
    if group_in == 'zeta':
        zeta.msgs(conn, uid)

def quit_room(conn, uid, group_in):
    if group_in == 'alpha':
        alpha.quit_rm(conn,uid)
    if group_in == 'beta':
        beta.quit_rm(conn,uid)
    if group_in == 'gamma':
        gamma.quit_rm(conn,uid)
    if group_in == 'omega':
        omega.quit_rm(conn,uid)
    if group_in == 'zeta':
        zeta.quit_rm(conn,uid)

def recieve_data(conn, address):
    while True:
        print('Waiting for instruction'.center(100,'-'))
        msg = conn.recv(2048)
        msg = str(msg,'utf-8')
        msg = msg.split(':')
        # Check the command and respond correctly
        if msg[0] == "1":
            list_files(conn, msg[1], msg[2])
        elif msg[0] == "2":
            upload(conn, address, msg[1], msg[2])
        elif msg[0] == "3":
            download(conn, address, msg[1], msg[2])
        elif msg[0] == "4":
            delete_file(conn, address, msg[1], msg[2])
        elif msg[0] == "5":
            share_file(conn, address, msg[1],msg[2],msg[3])
        elif msg[0] == "6":
            show_log(conn, msg[1],msg[2])
        elif msg[0] == "7":
            messages(conn, msg[1],msg[2])
        elif msg[0] == "8":
            quit_room(conn, msg[1],msg[2])
            break
        # Reset the data to loop
        msg = None

def recieve_command(conn, address):
    while True:
        msg = conn.recv(1024)
        msg = str(msg, 'utf-8')
        msg_list = msg.split(':')
        flag = True
        if msg_list[0] == '1':
            del msg_list[0]
            with codecs.open("data_file.csv", "r", 'utf-8') as csvfile:
                linereader = csv.reader(csvfile, delimiter=',', quotechar="\"")
                for row in linereader:
                    if msg_list[0] == row[1] and msg_list[1] == row[2]:
                        conn.send(str.encode('0'+':'+':'.join(row)))
                        print('Client with username: '+row[1]+' has logged in successfully!')
                        flag = False
                        break
                if flag:
                    print('There was a failed attempt!')
                    conn.send(str.encode('1'))
        if msg_list[0] == '2':
            del msg_list[0]
            print(msg_list)
            with codecs.open("data_file.csv", "r", 'utf-8') as csvfile:
                linereader = csv.reader(csvfile, delimiter=',', quotechar="\"")
                for row in linereader:
                    if msg_list[1] == row[1]:
                        conn.send(str.encode('0'))
                        flag = False
            if flag:
                with codecs.open('data_file.csv', 'a','utf-8') as csvfile:
                    linewriter = csv.writer(csvfile, delimiter=',', quotechar="\"")
                    linewriter.writerow(msg_list)
                    conn.send(str.encode('1'))
        if msg_list[0]== 'Group':
            with codecs.open("Groups.csv",'r','utf-8') as csvfile:
                linereader =csv.reader(csvfile,delimiter=',',quotechar='\"')
                for row in linereader:
                    conn.send(str.encode(':'.join(row)))
        if len(msg_list) >1 and msg_list[1] in GROUPS:
            if int(msg_list[2]) == 1:
                tempfile = NamedTemporaryFile(mode='w', delete=False)
                with codecs.open('data_file.csv', 'r','utf-8') as csvfile, tempfile:
                    reader = csv.reader(csvfile,delimiter=',',quotechar='\"')
                    writer = csv.writer(tempfile,delimiter=',',lineterminator = '\n',quotechar='\"')
                    for row in reader:
                        if row[1]==msg_list[0]:
                            row.append(msg_list[1])
                            if msg_list[1]=='alpha':
                                alpha.add_user(row[0],row[1])
                            if msg_list[1]=='beta':
                                beta.add_user(row[0],row[1])
                            if msg_list[1]=='gamma':
                                gamma.add_user(row[0],row[1])
                            if msg_list[1]=='omega':
                                omega.add_user(row[0],row[1])
                            if msg_list[1]=='zeta':
                                zeta.add_user(row[0],row[1])
                        writer.writerow(row)
                shutil.move(tempfile.name, 'data_file.csv')
            elif int(msg_list[2]) == 0:
                tempfile = NamedTemporaryFile(mode='w', delete=False)
                with codecs.open('data_file.csv', 'r','utf-8') as csvfile, tempfile:
                    reader = csv.reader(csvfile,delimiter=',',quotechar='\"')
                    writer = csv.writer(tempfile,delimiter=',',lineterminator = '\n',quotechar='\"')
                    for row in reader:
                        if row[1]==msg_list[0]:
                            row.remove(msg_list[1])
                            if msg_list[1]=='alpha':
                                alpha.del_user(row[0],row[1])
                            if msg_list[1]=='beta':
                                beta.del_user(row[0],row[1])
                            if msg_list[1]=='gamma':
                                gamma.del_user(row[0],row[1])
                            if msg_list[1]=='omega':
                                omega.del_user(row[0],row[1])
                            if msg_list[1]=='zeta':
                                zeta.del_user(row[0],row[1])
                        writer.writerow(row)
                shutil.move(tempfile.name, 'data_file.csv')
            elif int(msg_list[2]) == 2:
                if msg_list [1] == 'alpha':
                    conn.send(str.encode(alpha.welcome_msg()))
                if msg_list [1] == 'beta':
                    conn.send(str.encode(beta.welcome_msg()))
                if msg_list [1] == 'gamma':
                    conn.send(str.encode(gamma.welcome_msg()))
                if msg_list [1] == 'omega':
                    conn.send(str.encode(omega.welcome_msg()))
                if msg_list [1] == 'zeta':
                    conn.send(str.encode(zeta.welcome_msg()))


def start_lance():
    while True:
        cmd = input('lance>')
        if cmd == 'clear':
            print('\n'*50)
        elif cmd == 'list':
            list_saved_clients()
        else:
            print('command not recognized')


#Display all current saved clients in the json file
def list_saved_clients():
    with codecs.open("data_file.csv", "r",'utf-8') as csvfile:
        linereader = csv.reader(csvfile, delimiter=',', quotechar="\"")
        for row in linereader:
            print(row)

#Create worker threads
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()
#Do next job that is in the queue( handle connections, send commands)
def work():
    while True:
        x = queue.get()
        if x==1:
            create_socket()
            bind_socket()
            start_lance()
        if x==2:
            accept_command_connection()
        if x==3:
            accept_data_connection()

        queue.task_done()

def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)

    queue.join()

create_workers()
create_jobs()