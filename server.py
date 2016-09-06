import os
import http.server
from abc import ABCMeta, abstractmethod


class Case(metaclass=ABCMeta):
    @abstractmethod
    def test(self, handler):
        pass

    @abstractmethod
    def act(self, handler):
        pass

class case_directory_no_index_file(Case):
    '''Serve listing for the directory without an index file'''
    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')
    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               not os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.list_dir(handler.full_path)

class case_directory_index_file(Case):
    '''serve index.html for a directory!'''
    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')
    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               os.path.isfile(self.index_path(handler))
    def act(self, handler):
        handler.handle_file(self.index_path(handler))

class case_no_file(Case):
    ''' File or directory does not exists!'''
    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException("'{0}' not found!".format(handler.path))

class case_existing_file(Case):
    '''File exists!'''
    def test(self, handler):
        return os.path.isfile(handler.full_path)
    def act(self, handler):
        handler.handle_file(handler.full_path)

class case_always_fail(Case):
    '''Base case if nothing else worked!'''
    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("Unknown object '{0}'".format(handler.path))


class RequestHandler(http.server.BaseHTTPRequestHandler):

    '''\
    If requested file is found then its serverd!
    If anything else is happened error page is constructed!
    '''
    Cases = [case_no_file, case_existing_file, \
            case_directory_index_file, case_directory_no_index_file, case_always_fail]

    # listing directory page layout
    Listing_dir_page = '''\
        <html><body><ul>{0}</ul></body></html>
    '''

    Error_page = '''\
        <html>
            <body>
                <h1>Error accessing {path}</h1>
                <p>{msg}</p>
            </body>
        </html>

    '''

    # Handle a GET request.
    def do_GET(self):
        # page = self.create_page()
        # self.send_page(page)
        try:
            # figure out what is being requested.
            self.full_path = os.getcwd()+self.path

            # figure out how to handle.
            for case in self.Cases:
                # print(case.__name__)
                handler = case()
                if handler.test(self):
                    handler.act(self)
                    break
        # Handle errors
        except Exception as msg:
            self.handle_error(msg)

    def send_content(self, content, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def handle_file(self, full_path):
        try:
            with open(full_path, 'rb') as f:
                content = f.read()
            self.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read : {1}".format(self.path, msg)
            self.handle_error(msg)

    def list_dir(self, full_path):
        try:
            entries = os.listdir(full_path)
            bullets = ['<li>{0}</li>'.format(e) for e in entries if not e.startswith('.')]
            page = self.Listing_dir_page.format('\n'.join(bullets)).encode('utf-8')
            self.send_content(page)
        except Exception as msg:
            msg = "'{0}' cannot be listed: {1}".format(full_path, msg)
            self.handle_error(msg)

    # handle unknown object
    def handle_error(self, msg):
        content = self.Error_page.format(msg=msg, path=self.path).encode('utf-8')
        self.send_content(content, 404)

class ServerException(Exception):
    pass

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = http.server.HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()
