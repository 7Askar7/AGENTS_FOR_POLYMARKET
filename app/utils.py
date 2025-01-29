import os


def get_env(var_name: str) -> str:
    """
    Get an environment variable or raise an error if it is not set

    Args:
        var_name (str): The name of the environment variable

    Raises:
        ValueError: If the environment variable is not set

    Returns:
        str: The value of the environment variable
    """
    var = os.getenv(var_name)
    if var is None or var == "":
        raise ValueError(f"Environment variable {var_name} is not set")
    return var
