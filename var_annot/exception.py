"""
Exceptions specific to variant-annotation library.
"""


class PostError(Exception):
    def __init__(self, value, endpoint, headers, data):
        message = f"Error from POST, response code = {value}, endpoint = {endpoint}, headers = {headers}, data = {data}"
        super().__init__(message)
