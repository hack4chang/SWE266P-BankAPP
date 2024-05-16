import re

def is_valid_username(username):
    command_pattern = r'[^a-zA-Z0-9_.-]'  
    ip_pattern = r'(\d{1,3}\.){3}\d{1,3}'
    if re.search(command_pattern, username) or re.fullmatch(ip_pattern, username):
        return False
    return True

# Test cases
usernames = ["ls -la", "127.0.0.1", "normal_username", "another.user-name", "invalid|command"]

filtered_usernames = [uname for uname in usernames if is_valid_username(uname)]

print(filtered_usernames)  # Output should be: ['normal_username', 'another.user-name']


