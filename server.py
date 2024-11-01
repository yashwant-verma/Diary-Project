from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import json

# In-memory dictionary to store diary entries
diary_entries = {}

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Handle GET requests to serve HTML pages and CSS.
        """
        if self.path == '/':
            # Serve the welcome page
            self.serve_template('index.html')
        elif self.path.startswith('/search'):
            # Extract query parameters and search for entries
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            date = params.get('date', [None])[0]
            entries_html = self.generate_entries_html(date)
            self.serve_template('search_entry.html', {'entries_html': entries_html})
        elif self.path == '/add':
            # Serve the add entry page
            self.serve_template('add_entry.html')
        elif self.path == '/styles_index.css':
            self.send_css('styles_index.css')
        elif self.path == '/styles_add_entry.css':
            self.send_css('styles_add_entry.css')
        elif self.path == '/styles_search_entry.css':
            self.send_css('styles_search_entry.css')
        else:
            # Handle 404 Not Found
            self.send_response(404)
            self.end_headers()

    def send_css(self, css_path):
        """
        Send CSS files.
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/css')
        self.end_headers()
        with open(f'templates/{css_path}', 'rb') as file:
            self.wfile.write(file.read())

    def do_POST(self):
        """
        Handle POST requests to add diary entries.
        """
        if self.path == '/add':
            # Read and parse POST data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data = urllib.parse.parse_qs(post_data.decode())

            date = post_data.get('date', [None])[0]
            entry = post_data.get('entry', [None])[0]
            print("POST data received:", post_data)  # Debugging

            if date and entry:
                # Save the entry and redirect to the home page
                diary_entries[date] = entry
                self.send_response(302)
                self.send_header('Location', '/')
            else:
                # Handle missing data
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"Missing date or entry")
            self.end_headers()

    def search_entries(self, date):
        """
        Search for diary entries by date.
        """
        print("Searching for date:", date)  # Debugging
        entries = [{'date': date, 'entry': diary_entries[date]}] if date in diary_entries else []
        print("Entries retrieved:", entries)  # Debugging
        return entries

    def generate_entries_html(self, date):
        """
        Generate HTML for the search results.
        """
        entries = self.search_entries(date)
        if entries:
            entries_html = "<ul>"
            for entry in entries:
                entries_html += f"<li>{entry['date']}: {entry['entry']}</li>"
            entries_html += "</ul>"
        else:
            entries_html = "<p>No entries found for this date.</p>"
        return entries_html

    def serve_template(self, template_name, context=None):
        """
        Render and serve HTML templates without Jinja2.
        """
        with open(f'templates/{template_name}', 'r', encoding='utf-8') as file:
            content = file.read()
        if context:
            content = self.render_template(content, context)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(content.encode())

    def render_template(self, content, context):
        """
        Simple template rendering without Jinja2.
        """
        for key, value in context.items():
            placeholder = f'{{{{ {key} }}}}'
            content = content.replace(placeholder, str(value))
        return content

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    """
    Start the HTTP server.
    """
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
