class CustomError(Exception):
    """自定义错误"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)