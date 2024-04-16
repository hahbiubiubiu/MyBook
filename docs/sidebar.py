import os

def write_directory_structure(startpath):
    result = ''
    for root, dirs, files in os.walk(startpath):
        if root == './':
            continue
        for f in files:
            if f[:-3] in dirs:
                dirs.remove(f[:-3])
        root = root.replace('./', '/')
        level = root.replace(startpath, '').count(os.sep)
        indent = '  ' * (level)
        result += ('{}- {}\n'.format(indent, os.path.basename(root)))
        subindent = '  ' * (level + 1)
        for f in files:
            name = f.replace('.md', '')
            path = os.path.join(root, f.replace('.md', '')).replace('\\', '/')
            result += ('{}- [{}]({})\n'.format(subindent, name, path))
    return result


if __name__ == '__main__':
    startpath = './'  # 请修改为实际的开始路径
    content = write_directory_structure(startpath)
    print(content)
    with open('_sidebar.md', 'w', encoding='utf-8') as file:
        file.write(content)