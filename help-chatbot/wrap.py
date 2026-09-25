import sys
def wrap(html, marker):
    i = html.index(marker)
    head, body = html[:i], html[i:]
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<style>[hidden]{display:none!important}img{max-width:100%}body{margin:0}</style>\n' + head + '\n</head>\n<body>\n' + body + '\n</body>\n</html>\n')
if __name__ == '__main__':
    src, marker, out = sys.argv[1], sys.argv[2], sys.argv[3]
    html = open(src).read()
    open(out, 'w').write(wrap(html, marker))
