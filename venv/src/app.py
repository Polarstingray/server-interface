
from functools import wraps
import traceback
from flask import Flask, redirect, request, jsonify, url_for, render_template, Response
from server_api import ServerAPI
from logger import request_logger


app = Flask(__name__)

def expect_json(keys) :
    def decorator(f) :
        @wraps(f)
        def wrapper(*args, **kwargs) :
            data = request.get_json(silent=True) or {}
            missing = [k for k in keys if k not in data]
            if missing :
                return jsonify({"error" : f"Missing keys: {missing}"}), 400
            return f(data, *args, **kwargs)
        return wrapper
    return decorator

def log_exception(f) :
    @wraps(f)
    def wrapper(*args, **kwargs) :
        try :
            return f(*args, **kwargs)
        except Exception as e :
            print(traceback.format_exc())
            return jsonify({"error" : str(e)}), 500
    return wrapper

def server_api_route(route, methods=['GET']) :
    def decorator(f) :
        @app.route(f"/api{route}", methods=methods)
        @request_logger.log_request()
        @log_exception
        @wraps(f)
        def wrapper(*args, **kwargs) :
            result = f(*args, **kwargs)
            if isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], dict) and isinstance(result[1], int) :
                return jsonify(result[0]), result[1]
            return jsonify(result)
        return wrapper
    return decorator


def check_response(res) :
    if res['status'] != 0:
        return {"error": res['message']}, 500
    return res['data']

@app.route('/')
def index():
    return render_template('index.html')

#VM dashboard
@app.route('/vms')
def vm_dashboard() :
    return render_template('vms.html')

@server_api_route('/vms/list', methods=['GET'])
def list_vms() :
    res = ServerAPI.list_vms()
    return check_response(res)

@server_api_route('/vms/<name>', methods=['GET'])
def vm_info(name) :
    res = ServerAPI.vm_info(name)
    return check_response(res)

@server_api_route('/vms/<name>/state', methods=['GET'])
def vm_state(name) :
    res = ServerAPI.vm_state(name)
    return check_response(res)

@server_api_route('/vms/<name>/start', methods=['POST'])
def start_vm(name) :
    res = ServerAPI.start_vm(name)
    return check_response(res)

@server_api_route('/vms/<name>/stop', methods=['POST'])
def stop_vm(name) :
    res = ServerAPI.stop_vm(name)
    return check_response(res)

@server_api_route('/vms/<name>/reboot', methods=['POST'])
def reboot_vm(name) :
    res = ServerAPI.reboot_vm(name)
    return check_response(res)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


