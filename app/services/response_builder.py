class ResponseBuilder:
    def __init__(self):
        self.response = {
            "message": "",
            "status_code": 200,
            "data": None
        }

    def add_message(self, message: str):
        self.response["message"] = message
        return self

    def add_status_code(self, status_code: int):
        self.response["status_code"] = status_code
        return self

    def add_data(self, data):
        self.response["data"] = data
        return self

    def build(self):
        return self.response
