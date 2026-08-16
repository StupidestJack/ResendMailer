import lib.yaml as yaml
import lib.markdown2 as md
import subprocess
import uuid
import tempfile
from sys import exit as errexit
from shutil import copy2
from pathlib import Path
import resend

default = '''editor: vim
api_key: re_YourResendAPIKey
default_user: User <user@example.com>'''

config = yaml.safe_load(default)

def edit(filename):
    global config
    subprocess.run([config['editor'], filename])
    print('-' * 30)
    print("[1]Save to drafts then back")
    print("[2]Send")
    while True:
        inp = input("Please input: ")
        try:
            int(inp)
        except ValueError:
            print("Cannot turn input to a number. Please input a number.")
            continue
        else:
            option = int(inp)
            if option == 1:
                draft_menu()
                return
            elif option == 2:
                send_mail(filename)
                return
                
            

def send_mail(filename):
    global config

    path = Path(filename)
    content = path.read_text(encoding="utf-8")

    if not content.startswith("---"):
        print("Invalid mail format.")
        return

    parts = content.split("---", 2)
    if len(parts) < 3:
        print("Invalid mail front matter.")
        return

    params = yaml.safe_load(parts[1])
    body = parts[2].strip()

    html = md.markdown(body)

    resend.api_key = config["api_key"]

    try:
        email = resend.Emails.send({
            "from": params["from"],
            "to": params["to"],
            "subject": params["subject"],
            "html": html,
        })
    except Exception as e:
        print(f"Failed to send mail: {e}")
        return
    else:
        source = Path(filename)
        destination = Path("sent") / source.name

        source.rename(destination)

        print(f"Mail sent!")

def new_mail():
    global config
    filename = f"draft/{uuid.uuid4()}.md"
    Path(filename).touch()
    with open(filename, 'w') as f:
        f.write(f'''---
from: {config["default_user"]}
to:
 - user@example.com
subject: Input subject here!
---
''')
    edit(filename)

def draft_menu():
    while True:
        print('-' * 30)
        drafts = Path("draft")
        options = []
        for d in drafts.rglob('*.md'):
            content = d.read_text(encoding="utf-8")
            if not content.startswith("---"):
                continue
            
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue
            params = yaml.safe_load(parts[1])
            subject = params.get("subject", "(No subject)")
            options.append((d.stem, params.get("subject", "(No subject)")))
        
        length = len(options)
        chars_length = len(str(length))
        print(f"[{0:{chars_length}}]Back to main menu")
        for i in range(0, length):
            print(f"[{i+1:{chars_length}}]{options[i][1]}")
        inp = input("Please input: ")
        try:
            int(inp)
        except ValueError:
            print("Cannot turn input to a number. Please input a number.")
            continue
        else:
            option = int(inp)
            if option == 0:
                return
            else:
                if option > length or option < 0:
                    print("Please input a correct number.", end="")
                    continue
                else:
                    filename = options[option - 1][0]
                    edit(f'draft/{filename}.md')

def sent_menu():
    while True:
        print('-' * 30)
        sent_mails = Path("sent")
        options = []
        for d in sent_mails.rglob('*.md'):
            content = d.read_text(encoding="utf-8")
            if not content.startswith("---"):
                continue
            
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue
            params = yaml.safe_load(parts[1])
            subject = params.get("subject", "(No subject)")
            options.append((d.stem, params.get("subject", "(No subject)")))
        
        length = len(options)
        chars_length = len(str(length))
        print(f"[{0:{chars_length}}]Back to main menu")
        for i in range(0, length):
            print(f"[{i+1:{chars_length}}]{options[i][1]}")
        inp = input("Please input: ")
        try:
            int(inp)
        except ValueError:
            print("Cannot turn input to a number. Please input a number.")
            continue
        else:
            option = int(inp)
            if option == 0:
                return
            else:
                if option > length or option < 0:
                    print("Please input a correct number.", end="")
                    continue
                else:
                    filename = Path(f"sent/{options[option - 1][0]}.md")

                    with tempfile.TemporaryDirectory() as temp:
                        temp_file = Path(temp) / filename.name

                        # 複製一份到暫存區
                        copy2(filename, temp_file)

                        # 用使用者設定的 editor 開啟
                        subprocess.run(
                            [config["editor"], str(temp_file)],
                            check=True
                        )



def main_menu():
    print('-' * 30)
    print("[0]Exit")
    print("[1]Drafts")
    print("[2]Sent Mails")
    print("[3]New")
    while True:
        inp = input("Please input: ")
        try:
            int(inp)
        except ValueError:
            print("Cannot turn input to a number. Please input a number.")
            continue
        else:
            option = int(inp)
            if option == 0:
                exit()
            elif option == 1:
                draft_menu()
                break # 沒這個break就不會回到開頭顯示主選單選項
            elif option == 2:
                sent_menu()
                break
            elif option == 3:
                new_mail()
                break
            else:
                print("Please input a correct number.", end="")
        

if __name__ == '__main__':
    print('-' * 30)
    config_file = Path('config.yaml')
    if config_file.exists():
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    else:
        print('\'config.yaml\' not found, use default config.')
        with open('config.yaml', 'w') as f:
            f.write(default)
    
    Path("draft").mkdir(exist_ok=True)
    Path("sent").mkdir(exist_ok=True)

    print('Welcome to Niugnep\'s Resend Mailer!')
    while True:
        main_menu()
