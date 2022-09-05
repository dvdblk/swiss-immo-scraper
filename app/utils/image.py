"""Utilities for handling images / thumbnails"""

def scaled_image_size(width, height, max_width, max_height) -> tuple[float, float]:
    """Get a new image size given original w/h and given max w/h

    Note:
        https://stackoverflow.com/a/6501997/4249857
    """
    # Set default w/h if given is == 0
    if not width:
        width = 1024
    if not height:
        height = 728

    ratio_x = max_width / width
    ratio_y = max_height / height
    ratio = min(ratio_x, ratio_y)

    return width * ratio, height * ratio
