
import os
history_path = os.path.expandvars(r'%APPDATA%\Code\User\History')
target = 'def generate_top_students_image'
for root, dirs, files in os.walk(history_path):
    for f in files:
        if f.endswith('.json'): continue
        path = os.path.join(root, f)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                if target in fp.read():
                    print('FOUND_TARGET:', path)
        except:
            pass

