#! /usr/bin/env python
"""
    WSGI APP to convert wkhtmltopdf As a webservice

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import json
import tempfile

from werkzeug.wsgi import wrap_file
from werkzeug.wrappers import Request, Response
from executor import execute


@Request.application
def application(request):
    """
    To use this application, the user must send a POST request with
    base64 or form encoded encoded HTML content and the wkhtmltopdf Options in
    request data, with keys 'base64_html' and 'options'.
    The application will return a response with the PDF file.
    """
    if request.method != 'POST':
        return

    request_is_json = request.content_type.endswith('json')

    source_files = []
    # source_file = tempfile.NamedTemporaryFile(suffix='.html')
    
    payload = json.loads(request.data)

    pages = payload['contents']

    for page in pages:
        ptf = tempfile.NamedTemporaryFile(suffix='.html')
        ptf.write(page.decode('base64'))
        ptf.flush()
        source_files.append(ptf.name)

    # source_file.write(payload['contents'].decode('base64'))
    options = payload.get('options', {})

    if "header-html" in options:
        htf = tempfile.NamedTemporaryFile(suffix='.html')
        htf.write(options['header-html'].decode('base64'))
        htf.flush()
        options['header-html'] = htf.name

    if "footer-html" in options:
        ftf = tempfile.NamedTemporaryFile(suffix='.html')
        ftf.write(options['footer-html'].decode('base64'))
        ftf.flush()
        options['footer-html'] = ftf.name

    # source_file.flush()

    # Evaluate argument to run with subprocess
    args = ['wkhtmltopdf']

    # Add Global Options
    options['load-error-handling'] = 'ignore'
    if options:
        for option, value in options.items():
            args.append('--%s' % option)
            if value:
                args.append('"%s"' % value)

    # Add source file name and output file name
    # file_name = source_file.name
    file_name = source_files[0]
    args += source_files + [file_name + ".pdf"]

    # Execute the command using executor
    execute(' '.join(args))

    return Response(
        wrap_file(request.environ, open(file_name + '.pdf')),
        mimetype='application/pdf',
    )


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple(
        '127.0.0.1', 5000, application, use_debugger=True, use_reloader=True
    )
