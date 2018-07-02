import urllib
from app import app
from app.models import PatientDetails, OperationRecord, PractitionerDetails
from flask import jsonify, request, url_for

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

@app.route('/')
def index():
    data = jsonify({
            "message": "hello, welcome to Bethel alpha v0.0 have fun breaking the app.",
            "found-bugs": "please describe the actions you took and send the data you used so we can reproduce the bug. thank you!",
            "site-map": url_for('site_map')
        })
    return data

@app.route("/site-map")
def site_map():
    links = []
    output = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        if not 'filename' in options:
            print (options)

        if "GET" in rule.methods and has_no_empty_params(rule):
            methods = ','.join(rule.methods)
            url = url_for(rule.endpoint, **options)
            links.append((url, rule.endpoint, methods))
            line = urllib.unquote("{:20s} {}".format(methods, url))
            output.append(line)
    # links is now a list of url, endpoint tuples
    return jsonify(output)

@app.errorhandler(404)
@app.errorhandler(405)
def _handle_api_error(ex):
    if request.path.startswith('/api/'):
        return jsonify({"error": "resources not found"})
    else:
        return ex
