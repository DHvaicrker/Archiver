from tempfile import mkdtemp
import shutil
def with_temp_dir(func):
    """Decorator that creates a temporary directory before calling the function
       and deletes it after the function execution (regardless of exceptions).

    Args:
        func: The function to be decorated.
    """

    def wrapper(*args, **kwargs):
        """Wrapper function that manages the temporary directory."""
        temp_dir = mkdtemp()
        temp_dir = temp_dir.replace("\\","/")
        try:
            # Pass the temporary directory path as a keyword argument
            kwargs["temp_dir"] = temp_dir
            return func(*args, **kwargs)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)  # Delete temp_dir always
    return wrapper
def password_check(func):

    def wrapper(*args, **kwargs):
        """Wrapper function that manages the passwords and if password wasnt given create a default one."""
        if "password" not in kwargs:
            kwargs["password"] = "".encode()
        else:
            kwargs["password"] = kwargs["password"].encode()

        return func(*args, **kwargs)

    return wrapper
