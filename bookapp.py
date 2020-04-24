import re
import traceback

from bookdb import BookDB

DB = BookDB()


def book(book_id):
    bookinfo = DB.title_info(book_id)
    if bookinfo is None:
        raise NameError
    title = bookinfo['title']
    body = [f'<h1>{title}</h1>', '<table>']
    for key in bookinfo.keys():
        if not key == 'title':
            body.append(f'<tr><th>{key.title()}</th><td>{bookinfo[key]}</td></tr>')
    body.extend(['</table>', '<a href="/">Back to the list</a>'])
    return '\n'.join(body)#"<h1>a book with id %s</h1>" % book_id


def books():
    body = ['<h1>Book Shelf</h1>', '<ul>']
    for book in DB.titles():
        link = f'<li><a href="/book/{book["id"]}">{book["title"]}</a></li>'
        # link = '<li><a href="/book/' + book['id'] + '">' + book['title'] + '</a></li>'
        body.append(link)
    body.append('</ul>')
    body = '\n'.join(body)
    return body


def resolve_path(path):
    funcs = {
            '': books,
            'book': book
            }

    path = path.strip('/').split('/')

    func_name = path[0]
    args = path[1:]

    try:
        func = funcs[func_name]
    except KeyError:
        raise NameError

    return func, args


def application(environ, start_response):
    headers = [('Content-type', 'text/html')]
    try:
        path = environ.get('PATH_INFO', None)
        if path is None:
            raise NameError
        func, args = resolve_path(path)
        body = func(*args)
        status = "200 OK"
    except NameError:
        status = '404 Not Found'
        body = '<h1> Not Found </h1>'
    except Exception:
        status = '500 Internal Server Error'
        body = '<h1>Internal Server Error</h1>'
        print(traceback.format_exc())
    finally:
        headers.append(('Content-length', str(len(body))))
        start_response(status, headers)
        return [body.encode('utf8')]


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, application)
    srv.serve_forever()
