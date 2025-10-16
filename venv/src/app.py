
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
        return format_response(1, res['message'], res['data'])
    return format_response(0, res['message'], res['data'])
    

def format_response(status, message, data):
    status_out = False
    data_key = "error"
    if status == 0:
        data_key = "data"
        status_out = True
    
    return {
        "status" : status_out,
        "message" : message,
        data_key : data
    }

@app.route('/')
def index():
    return render_template('index.html')

#VM dashboard
@app.route('/vm')
def vm_dashboard() :
    return render_template('vm.html')

@server_api_route('/vm/list', methods=['GET'])
def list_vms() :
    res = ServerAPI.list_vms()
    return check_response(res)

@server_api_route('/vm/<name>', methods=['GET'])
def vm_info(name) :
    res = ServerAPI.vm_info(name)
    return check_response(res)

@server_api_route('/vm/<name>/state', methods=['GET'])
def vm_state(name) :
    res = ServerAPI.vm_state(name)
    return check_response(res)

@server_api_route('/vm/<name>/start', methods=['POST'])
def start_vm(name) :
    res = ServerAPI.start_vm(name)
    return check_response(res)

@server_api_route('/vm/<name>/stop', methods=['POST'])
def stop_vm(name) :
    res = ServerAPI.stop_vm(name)
    return check_response(res)

@server_api_route('/vm/<name>/reboot', methods=['POST'])
def reboot_vm(name) :
    res = ServerAPI.reboot_vm(name)
    return check_response(res)

@server_api_route('/vm/create', methods=['POST'])
@expect_json(["name", "memory", "vcpus", "os", "network", "disk_path", "iso"])
def create_vm(data) :
    res = ServerAPI.create_vm(data)
    return check_response(res)

@server_api_route('/history', methods=['GET'])
def get_history():
    res = ServerAPI.get_history()
    return check_response(res)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

