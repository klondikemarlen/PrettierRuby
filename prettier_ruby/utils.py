import locale
import os
import platform
import shutil


def is_windows():
    return platform.system() == "Windows" or os.name == "nt"


def decode_bytes(bytes_to_decode):
    """
    Decode and return a byte string using utf-8, falling back to system's encoding if that fails.

    Source: Sublime Linter
    https://github.com/SublimeLinter/SublimeLinter/blob/master/lint/util.py#L272
    """
    if not bytes_to_decode:
        return ""

    try:
        return bytes_to_decode.decode("utf-8")
    except UnicodeError:
        return bytes_to_decode.decode(locale.getpreferredencoding(), errors="replace")


def format_error_message(error_message, error_code):
    # inject a line break between the error message, and debug output (legibility purposes):
    error_message = error_message.replace("[error] stdin: ", "\n[error] stdin: ")

    return (
        "\nPrettier reported the following output:\n\n"
        "{0}\n"
        "\nPrettier process finished with exit code {1}.\n".format(
            error_message, "{0}".format(error_code)
        )
    )


def env_path_contains(path_to_look_for, env_path=None):
    """Check if the specified path is listed in OS environment path.

    :param path_to_look_for: The path the search for.
    :param env_path: The environment path str.
    :return: True if the find_path exists in the env_path.
    :rtype: bool
    """
    if not path_to_look_for:
        return False
    if not env_path:
        env_path = os.environ["PATH"]
    path_to_look_for = str.replace(path_to_look_for, os.pathsep, "")
    paths = env_path.split(os.pathsep)
    for path in paths:
        if path == path_to_look_for:
            return True
    return False


def env_path_exists(path):
    if not path:
        return False
    if os.path.exists(str.replace(path, os.pathsep, "")):
        return True
    return False


def upsert_path(path, new_entry):
    if not env_path_contains(new_entry, path) and env_path_exists(new_entry):
        return ":".join([new_entry, path])
    return path


def get_proc_env(additional_paths=None):
    additional_paths = [] if additional_paths is None else additional_paths

    env = None
    if not is_windows():
        env = os.environ.copy()
        env["PATH"] = upsert_path(env["PATH"], "/usr/local/bin")
        for path in reversed(additional_paths):
            env["PATH"] = upsert_path(env["PATH"], path)

    return env


def normalize_line_endings(lines):
    if not lines:
        return lines
    return lines.replace("\r\n", "\n").replace("\r", "\n")


def ensure_file_has_ext(file_name, file_ext):
    if not file_name.endswith(file_ext):
        return "{0}{1}".format(file_name, file_ext)
    return file_name


def is_str_none_or_empty(val):
    """Determine if the specified str val is None or an empty.

    :param val: The str to check.
    :return: True if if val: is None or an empty, otherwise False.
    :rtype: bool
    """
    if val is None:
        return True
    if isinstance(val, string_types):
        val = val.strip()
    if not val:
        return True
    return False


def which(command, working_directory=None):
    path = os.defpath
    if working_directory:
        path = ":".join([working_directory, path])

    return shutil.which(command, path=path)


def resolve_path(command, working_directory, default=None):
    command_path = which(command, working_directory)
    if command_path:
        return command_path

    if default:
        return default

    raise EnvironmentError(
        "Could not determine path for command: {command}".format(command=command)
    )
