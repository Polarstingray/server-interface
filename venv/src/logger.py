# Written with the help of ChatGPT

import logging
from datetime import datetime
from functools import wraps
from flask import request
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOG_DIR = os.path.join(ROOT_DIR, 'logs')

class RequestLogger:
    def __init__(self, log_dir=LOG_DIR):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Create main request logger
        self.request_logger = logging.getLogger('request_logger')
        self.request_logger.setLevel(logging.INFO)

        # Create handlers for different log types
        self._setup_handlers()

    def _setup_handlers(self):
        # Request log handler
        request_handler = logging.FileHandler(f'{self.log_dir}/requests.log')
        request_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.request_logger.addHandler(request_handler)

        # Error log handler
        error_handler = logging.FileHandler(f'{self.log_dir}/errors.log')
        error_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        error_handler.setLevel(logging.ERROR)
        self.request_logger.addHandler(error_handler)

    def log_request(self):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                # Log request details
                start_time = datetime.now()
                request_data = {
                    'method': request.method,
                    'path': request.path,
                    'ip': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent'),
                    'data': request.get_json(silent=True) if request.is_json else None,
                    'args': dict(request.args)
                }

                try:
                    # Execute the route function
                    response = f(*args, **kwargs)
                    
                    # Calculate request duration
                    duration = (datetime.now() - start_time).total_seconds()

                    # Log successful request
                    self.request_logger.info(
                        f"REQUEST: {request_data['method']} {request_data['path']} - "
                        f"IP: {request_data['ip']} - "
                        f"Duration: {duration:.2f}s - "
                        f"Status: {response[1] if isinstance(response, tuple) else 200}"
                    )

                    return response

                except Exception as e:
                    # Log error
                    self.request_logger.error(
                        f"ERROR in {request_data['method']} {request_data['path']} - "
                        f"IP: {request_data['ip']} - "
                        f"Error: {str(e)}",
                        exc_info=True
                    )
                    raise

            return wrapper
        return decorator

# Create singleton instance
request_logger = RequestLogger()    