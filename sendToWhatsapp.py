import json
import os
import subprocess
import pywhatkit as kit
import time
from cryptography.fernet import Fernet
import platform
import webbrowser

# File to store hosts data and encrypted password
HOSTS_FILE = 'hosts.json'

# Hardcoded encryption key
KEY = b'WFljjHCnwwyv_Z2U0abKGl3QtIUFvd6Mi0s6l9299pY='

# Initialize Fernet with the hardcoded key
fernet = Fernet(KEY)

def decrypt_data(encrypted_data, fernet):
    return fernet.decrypt(encrypted_data).decode()

def load_hosts(fernet):
    if os.path.exists(HOSTS_FILE):
        with open(HOSTS_FILE, 'rb') as file:
            encrypted_data = file.read()
            decrypted_data = decrypt_data(encrypted_data, fernet)
            return json.loads(decrypted_data)
    return {}

# Function to ping an IP address and return the result with a symbol
def ping_host(ip_address):
    try:
        if platform.system().lower() == 'windows':
            output = subprocess.check_output(['ping', '-n', '1', ip_address], stderr=subprocess.STDOUT, universal_newlines=True)
            if 'Reply from' in output:
                return '✅Responding'
            else:
                return '❌NOT Responding'
        else:
            output = subprocess.check_output(['ping', '-c', '1', ip_address], stderr=subprocess.STDOUT, universal_newlines=True)
            if '1 packets transmitted, 1 received' in output:
                return '✅Responding'
            else:
                return '❌NOT Responding'
    except subprocess.CalledProcessError:
        return '❌NOT Responding'

def send_to_whatsapp_group(group_id, message):
    kit.sendwhatmsg_to_group_instantly(group_id, message, 20)
    # Wait for a few seconds to ensure the message is sent
    time.sleep(120)
    # Close the browser window
    if platform.system().lower() == 'windows':
        os.system("taskkill /im chrome.exe /f")
    else:
        os.system("pkill chrome")

def main():
    # Load existing hosts data
    hosts = load_hosts(fernet)
    print(hosts)

    group_id = "FyvQpcCS52v01GbScixKJp"  # Replace with your WhatsApp group ID
    
    # Prepare initial message
    initial_message = "Initial Host Status Report:\n"
    non_responding_hosts = []
    
    for host, ip in hosts.items():
        status = ping_host(ip)
        if status == '❌NOT Responding':
            non_responding_hosts.append(f"{host} is: {status}")
        else:
            initial_message += f"{host} is: {status}\n"
    
    # Send initial message to WhatsApp group
    if non_responding_hosts:
        non_responding_message = "Non-Responding Hosts:\n" + "\n".join(non_responding_hosts)
        send_to_whatsapp_group(group_id, non_responding_message)
    else:
        send_to_whatsapp_group(group_id, "All registered hosts are responding.")

    # Track the previous statuses
    previous_statuses = {host: ping_host(ip) for host, ip in hosts.items()}
    
    while True:
        current_statuses = {}
        status_changes = []
        
        # Check current statuses
        for host, ip in hosts.items():
            status = ping_host(ip)
            current_statuses[host] = status
            if previous_statuses[host] != status:
                status_changes.append(f"{host} ({ip}): {status}")
                previous_statuses[host] = status
        
        # Send status change messages
        if status_changes:
            change_message = "Status Change Report:\n" + "\n".join(status_changes)
            send_to_whatsapp_group(group_id, change_message)
        
        # Wait for 5 minute
        time.sleep(300)
        print("Waiting for the next iteration...")

if __name__ == "__main__":
    main()
