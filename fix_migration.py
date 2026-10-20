import glob, os

files = glob.glob('backend/migrations/versions/*add_retraining_jobs_table.py')
file_path = files[0]

with open(file_path, 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if 'op.alter_column' in line:
        skip = True
    if skip:
        if line.strip() == ')':
            skip = False
        continue
    new_lines.append(line)

with open(file_path, 'w') as f:
    f.writelines(new_lines)
