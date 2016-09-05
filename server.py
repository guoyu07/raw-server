import http.server


class RequestHandler(http.server.BaseHTTPRequestHandler):
    '''Handle HTTP request by sending a fixed 'page'. '''
    # page to send back
    page = b'''\
        <html>
            <body>
                <p>We are on web!</p>
            </body>
        </html>
    '''

    # Handle a GET request.
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(self.page)))
        self.end_headers()
        self.wfile.write(self.page)

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = http.server.HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()
