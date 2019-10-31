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
import socket
import os
import sys
import subprocess
import time
import struct
from termcolor import colored

host = '10.1.135.169'
command_port = 9999
data_port = 8488
cs = socket.socket()
try:
    cs.connect((host, command_port))
except:
    pass

class user:
    def __init__(self,username,userId,group_list):
        self._uname = username
        self._uid = userId
        self._groups = group_list

    def uname(self):
        return self._uname
    def uid(self):
        return self._uid
    def gno(self):
        return len(self._groups)
    def add_group(self, group_in):
        self._groups.append(group_in)
    def del_group(self, group_in):
        self._groups.remove(group_in)
    def group_list(self):
        return self._groups


def list_files(ds,uid, group_in):
    print('Listing files...\n')
    try:
        ds.send(str.encode('1'+':'+uid+':'+group_in))
    except:
        print("Couldn't make server request. Make sure a connection has been established.")
        return
    try:
        number_of_files = struct.unpack("i", ds.recv(4))[0]
        for i in range(int(number_of_files)):
            file_info = str(ds.recv(1024),'utf-8')
            file_info = file_info.split(':')
            print("\t{} - {}b".format(file_info[0], file_info[1]))
            ds.send(str.encode("1"))
        total_directory_size = struct.unpack("i", ds.recv(4))[0]
        print("Total directory size: {}b".format(total_directory_size))
    except:
        print("Couldn't retrieve listing")
        return
    try:
        ds.send(str.encode("1"))
        return
    except:
        print("Couldn't get final server confirmation")
        return

def upload(ds,dir_name,uid,group_in):
    print('Uploading the file {}'.format(dir_name))
    ds.send(str.encode('2'+':'+uid+':'+group_in))
    try:
        content = open(dir_name, "rb")
    except:
        print("Couldn't open file. Make sure the file name was entered correctly.")
        return
    try:
        ds.recv(1024)
        ds.send(struct.pack("h", sys.getsizeof(dir_name)))
        ds.send(str.encode(dir_name))
        ds.recv(2048)
        ds.send(struct.pack("i", os.path.getsize(dir_name)))
    except:
        print('Error sending file details')
    try:
        l = content.read(1024)
        print("\nUploading...")
        while l:
            ds.send(l)
            l = content.read(1024)
        content.close()
        upload_time = struct.unpack("f", ds.recv(4))[0]
        upload_size = struct.unpack("i", ds.recv(4))[0]
        print('\nSent file: {}\nTime elapsed: {}s\nFile size: {}b'.format(dir_name, upload_time, upload_size))
    except:
        print('Error sending file')
        return
    return

def download(ds,f_name,uid,group_in):
    file_size = 0
    print("Downloading file: {}".format(f_name))
    try:
        ds.send(str.encode('3'+':'+uid+':'+group_in))
    except:
        print("Couldn't make server request. Make sure a connection has bene established.")
        return
    try:
        ds.recv(1024)
        ds.send(struct.pack("h", sys.getsizeof(f_name)))
        ds.send(str.encode(f_name))
        file_size = struct.unpack("i", ds.recv(4))[0]
        if file_size == -1:
            print('File does not exist. Make sure the name was entered correctly')
            return
    except:
        print('Error checking file')
    try:
        ds.send(str.encode('1'))
        output_file = open(f_name, "wb")
        bytes_recieved = 0
        print('\nDownloading...')
        while bytes_recieved < file_size:
            l = ds.recv(1024)
            output_file.write(l)
            bytes_recieved += 1024
        output_file.close()
        print('Successfully downloaded {}'.format(f_name))
        ds.send(str.encode('1'))
        time_elapsed = struct.unpack("f", ds.recv(4))[0]
        print('Time elapsed: {}s\nFile size: {}b'.format(time_elapsed, file_size))
    except:
        print('Error downloading file')
        return
    return

def delete_file(ds,f_name,uid,group_in):
    print('Deleting file: {}...'.format(f_name))
    try:
        ds.send(str.encode('4'+':'+uid+':'+group_in))
        ds.recv(1024)
    except:
        print("Couldn't connect to server.")
        return
    try:
        ds.send(struct.pack("h", sys.getsizeof(f_name)))
        ds.send(str.encode(f_name))
    except:
        print("Couldn't send file details")
        return
    try:
        file_exists = struct.unpack("i", ds.recv(4))[0]
        if file_exists == -1:
            print('The file does not exist on server')
            return
    except:
        print("Couldn't determine file existence")
        return
    try:
        confirm_delete = input("Are you sure you want to delete {}? (Y/N)\n".format(f_name)).lower()
        while confirm_delete != "y" and confirm_delete != "n":
            print('Command not recognised!')
            confirm_delete = input("Are you sure you want to delete {}? (Y/N)\n".format(f_name)).lower()
    except:
        print("Couldn't confirm deletion status")
        return
    try:
        if confirm_delete == "y":
            ds.send(str.encode('Y'))
            delete_status = struct.unpack("i", ds.recv(4))[0]
            if delete_status == 1:
                print('File successfully deleted')
                return
            else:
                print('File failed to delete')
                return
        else:
            ds.send(str.encode("N"))
            print('Delete abandoned by user!')
            return
    except:
        print("Couldn't delete file")
        return

def share_file(ds,f_name,uid,group_in,g_name):
    ds.send(str.encode('5' + ':' + uid + ':' + group_in+':'+g_name))
    msg = ds.recv(1024)
    msg = str(msg,'utf-8')
    if msg == '0':
        print('You cannot share to that group!')
        return
    print('File Shared to {}'.format(g_name))
    return

def show_log(ds,uid, group_in):
    ds.send(str.encode('6' + ':' + uid + ':' + group_in))
    msg = ds.recv(2048)
    msg = str(msg, 'utf-8')
    print(msg)
    return

def messages(ds,uid, group_in):
    ds.send(str.encode('7' + ':' + uid + ':' + group_in))
    """
    msg = ds.recv(2048)
    msg = str(msg, 'utf-8')
    print(msg)
    """
    print(colored("Press any key to send(type 'quit' if you want to leave): ".center(100),'magenta'))
    while True:
        msg = ds.recv(2048)
        msg = str(msg, 'utf-8')
        print(msg,flush=True)
        msg_data = input(newUser.uid() + '>')
        if len(msg_data)>0:
            if msg_data.lower() != 'quit':
                print('Sending the message... ')
                ds.send(str.encode(msg_data))
            else:
                print('Leaving...')
                ds.send(str.encode(msg_data))
                break
    return

def quit_room(ds,uid, group_in):
    ds.send(str.encode('8' + ':' + uid + ':' + group_in))
    return

#crucial chatroom function
def enter_chatroom(newUser, group_in):
    ds = socket.socket()
    try:
        ds.connect((host, data_port))
    except:
        pass
    cs.send(str.encode(newUser.uid() + ':' + group_in + ':' + str(2)))
    msg = cs.recv(2048)
    msg = str(msg,'utf-8')
    print('\n'*50)
    print(colored(msg,'green').center(100))
    print()
    while True:
        print()
        print("1. List Files\n2 .Upload File\n3. Download File\n4. Delete File\n5. Share File\n6. Show Log\n7. Messages\n8. Leave Chatroom")
        client_in = input("\nEnter a command: ")
        if client_in == "1":
            list_files(ds,newUser.uid(), group_in)
        elif client_in == "2":
            dir_name = input('Enter the path of the file to upload: ')
            upload(ds,dir_name,newUser.uid(),group_in)
        elif client_in == "3":
            f_name = input('Enter the name of the file to download: ')
            download(ds,f_name,newUser.uid(),group_in)
        elif client_in == "4":
            f_name = input('Enter the name of the file to delete: ')
            delete_file(ds,f_name,newUser.uid(),group_in)
        elif client_in == "5":
            f_name = input('Enter the name of the file to share: ')
            g_name = input('Enter the name of the group you are part of to share: ')
            share_file(ds,f_name,newUser.uid(),group_in,g_name)
        elif client_in == "6":
            show_log(ds,newUser.uid(), group_in)
        elif client_in == "7":
            messages(ds,newUser.uid(), group_in)
        elif client_in == "8":
            quit_room(ds,newUser.uid(), group_in)
            ds.close()
            break
        else:
            print("Invalid Input!")

def user_dashboard(newUser):
    #cs = socket.socket()
    #cs.connect((host,command_port))
    print('Logged in successfully!'.center(100))
    print(('Welcome ' + newUser.uname()).center(100))
    for i in range(20):
        print('~~~~~', flush=True, end='')
        time.sleep(.05)
    print('\n'*50)
    print(colored('Lance','blue').center(100,'-'))
    print(('Name: '+newUser.uname()).rjust(100))
    print(('Groups joined('+str(newUser.gno())+')').rjust(100))
    cs.send(str.encode('Group'))
    msg = cs.recv(1024)
    msg = str(msg,'utf-8')
    msg = msg.split(':')
    print('Active Groups are: '+colored(', '.join(msg),'red'))
    print('\n'*1)
    while True:
        i = input('Enter a command'.center(100)+'\n1.List Group\n2.Join Group\n3.Leave Group\n4.Sign out\n')
        if i == '1':
            if newUser.gno() ==0:
                print('You are not part of any groups! You can join the groups: '+colored(', '.join(msg),'red'))
            else:
                while True:
                    print('Yor are part of these groups: '+colored(', '.join(newUser.group_list()),'red'))
                    group_in = input('Enter the name of the group you wish to enter: ')
                    if group_in in newUser.group_list():
                        print('Entering the group'.center(100))
                        for i in range(20):
                            print('~~~~~', flush=True, end='')
                            time.sleep(.05)
                        enter_chatroom(newUser, group_in)
                        break
                    else:
                        print('Invalid Input!')
        elif i == '2':
            if newUser.gno() == len(msg):
                print('You cannot join any more groups!')
            else:
                groups_left = [item for item in msg if item not in newUser.group_list()]
                print('You can join the groups: ' + colored(', '.join(groups_left),'red'))
                while True:
                    group_in = input('Enter the name of the group you want to join: ')
                    if group_in in groups_left:
                        break
                    else:
                        print('Enter valid group name(case sensitive): '+colored(', '.join(msg),'red'))
                cs.send(str.encode(newUser.uid()+':'+group_in+':'+str(1)))
                newUser.add_group(group_in)
                enter_prompt = input('Do you wish to enter {} (Y/N)'.format(colored(group_in,'red')))
                if enter_prompt.upper() == 'Y':
                    print('Entering the group'.center(100))
                    for i in range(20):
                        print('~~~~~', flush=True, end='')
                        time.sleep(.05)
                    enter_chatroom(newUser, group_in)
                else:
                    pass
        elif i == '3':
            if newUser.gno() == 0:
                print('Please join a group first.')
            else:
                while True:
                    group_in = input('Enter a group name you want to leave({}): '.format(colored(', '.join(newUser.group_list()),'red')))
                    if group_in in newUser.group_list():
                        cs.send(str.encode(newUser.uid()+':'+group_in+':'+str(0)))
                        newUser.del_group(group_in)
                        print('You left {} group!'.format(group_in))
                        break
                    else:
                        print('Enter a valid group name!')
        elif i == '4':
            print('\n'*3)
            print('Signing Out'.center(100,'*'))
            for i in range(20):
                print('~~~~~', flush=True, end='')
                time.sleep(.05)
            break
        else:
            print('Invalid command')


while True:
    print('\n'*50)
    print(colored('Lance','blue').center(100, '-'))
    print('\n' * 3)
    i = input('Enter a command'.center(100)+ "\n1. Sign In\n" + "2. Sign Up\n" + "3. Exit\n")
    flag = str(i)
    if i=='1':
        username = input('Username: ')
        password = input('Password: ')
        data = str(flag +':'+ username + ':' + password)
        cs.send(str.encode(data))
        msg = str(cs.recv(1024), 'utf-8')
        msg = msg.split(':')
        group_list = []
        if len(msg)>4 :
            for i in range(4,len(msg)):
                group_list.append(msg[i])       #appending the groups joined by the client
        if not int(msg[0]):
            newUser = user(msg[1],msg[2],group_list)
            user_dashboard(newUser)
        else:
            print('Invalid Credentials!')
            for i in range(20):
                print('~~~~~', flush=True, end='')
                time.sleep(.05)
    elif i=='2':
        name = input('Name: ')
        username = input('Username: ')
        password = input('Password: ')
        data = str(flag +':'+ name + ':' + username + ':'+ password)
        cs.send(str.encode(data))
        msg = int(str(cs.recv(1024),'utf-8'))
        if msg:
            print('Registered Successfully')
        else:
            print('Username already exists')
    elif i=='3':
        break
    else:
        print("Invalid Command")