
def single_user_input(question: str):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            user_input = input(f'{question}')
            result = func(self, user_input, *args, **kwargs)
            return result
        return wrapper
    return decorator
