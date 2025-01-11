from .logger import Logger


def get_file_size_input():
    """
    prompts the user for a file size until input is valid.
    supported formats: <int>GB, <int>MB, <int>KB, <int>G, <int>M, <int>K, <int>B, <int>
    :return:
        size: file size in bytes
    """
    file_size = input("File size: ")

    if file_size.isdigit():
        return int(file_size)
    elif file_size[0:-1].isdigit():
        size = int(file_size[0:-1])
        match file_size[-1].upper():
            case "G":
                return size * 1024 * 1024 * 1024
            case "M":
                return size * 1024 * 1024
            case "K":
                return size * 1024
            case "B":
                return size
    elif file_size[0:-2].isdigit():
        unit = file_size[-2:].upper()
        size = int(file_size[0:-2])

        match unit:
            case "GB":
                return size * 1024 * 1024 * 1024
            case "MB":
                return size * 1024 * 1024
            case "KB":
                return size * 1024

    Logger.warn("Invalid value. please provide a valid file size in GB/MB/KB/B")
    return get_file_size_input()


def get_int(msg):
    """
    prompt the user for an int until input is valid
    :param msg:
        message to display while prompting
    :return:
        value: int input
    """
    value = input(msg)
    if not value.isdigit():
        Logger.warn("Invalid Value. Must be an integer.")
        return get_int(msg)
    return value