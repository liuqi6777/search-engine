import os

from bs4 import BeautifulSoup


doc_path = '../doc/'
html_path = doc_path + 'raw/'
txt_path = doc_path + 'text/'


# 读取html文件
def read_html(html_file, encoding='utf-8'):
    with open(html_file, 'r', encoding=encoding) as f:
        html_text = f.read()
    return html_text


# 提取html文本内的标题
def extract_title(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return str(soup.find('title'))[7:-8].replace('<br>', '')


# 提取html文本内的所有文本
def extract_body(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.strings


# 把html文件内的所有文本内容输出到txt文件中
def html_to_txt(html_file, txt_file):
    text = extract_body(read_html(html_file))
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.writelines(text)
        

if __name__ == '__main__':
    all_file = os.listdir(html_path)
    for file in all_file:
        if os.path.splitext(file)[1] == '.html':
            t = os.path.join(txt_path, os.path.splitext(file)[0]+'.txt')
            html_to_txt(os.path.join(html_path, file), t)
