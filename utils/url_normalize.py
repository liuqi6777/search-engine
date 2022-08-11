import urllib.parse as parse

"""
完整的url语法格式：
协议://用户名@密码:子域名.域名.顶级域名:端口号/目录/文件名.文件后缀?参数=值#标识
scheme:[//[user:password@]host[:port]][/]path[?query][#fragment]
"""


# 字符串规划化
def url_normalize(url):
    url = url.replace('\n', '').replace(' ', '')
    url = parse.unquote(url)
    url = parse.urlparse(url)

    scheme = url.scheme
    netloc = url.netloc
    path = url.path
    params = url.params
    query = url.query
    q = parse.parse_qsl(query)
    fragment = ''

    # 协议名小写
    scheme = scheme.lower()

    # 统一移除www.
    netloc = netloc.lower()
    if netloc.find('www.') != -1:
        netloc = netloc.replace('www.', '')

    # 移除index.html
    if path.find('index.html') != -1:
        path = path.replace('index.html', '')
    if path.find('index.htm') != -1:
        path = path.replace('index.htm', '')

    # 删除多余的点
    output, part = [], None
    for part in path.split("/"):
        if part == "":
            if not output:
                output.append(part)
        elif part == ".":
            pass
        elif part == "..":
            if len(output) > 1:
                output.pop()
        else:
            output.append(part)
    if part in ["", ".", ".."]:
        output.append("")
    path = "/".join(output).strip()

    # 把query统一格式，这里将默认值删去，并字典序排序
    query = '&'.join(['='.join(i) for i in sorted(q)]).strip()
    
    url = [scheme, netloc, path, params, query, fragment]
    url = str(parse.urlunparse(url)).strip()
    return url


if __name__ == '__main__':

    test = ['HTTP://WWW.EXAMPLE.com', 'http://www.example.com/test/index.html#seo',
            'http://www.example.com/test?', 'http://www.example.com/test/index.html',
            'http://www.example.com/../a/b/../c/./d.html', 'http://www.test.example.com/',
            'http://www.example.com/test?id=123&fakefoo=fakebar', 'http://www.example.com/test?id=&sort=ascending',
            'http://www.example.com/test?', 'http://www.example.com/test?id=123']

    for test_url in test:
        print(test_url)
        print(parse.unquote(test_url))
        print(parse.urlparse(test_url))
        print(url_normalize(test_url))
        print('')
