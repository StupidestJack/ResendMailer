import lib.yaml as yaml
import lib.markdown2 as md
import subprocess
from pathlib import Path

config_file = Path('config.yaml')
config = yaml.safe_load('''editor: vim
api_key: re_abcdefg''')
if config_file.exists():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
else:
    print('\'config.yaml\' not found, use default config.')

print('Welcome to Niugnep\'s Resend Mailer!')