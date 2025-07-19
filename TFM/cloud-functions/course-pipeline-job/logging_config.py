import logging
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': self.formatTime(record),
            'severity': record.levelname,
            'message': record.getMessage(),
            'logger': record.name
        }
        if hasattr(record, 'funcName'):
            log_entry['function'] = record.funcName
        if hasattr(record, 'lineno'):
            log_entry['line'] = record.lineno
        return json.dumps(log_entry)

def setup_json_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler) 