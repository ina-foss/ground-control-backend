"""
Utility functions for converting segment data into task formats.
"""

import json


def convert(segments):
    """
    Convert segment data into a JSON-formatted task structure.

    Args:
        segments (list): The segment data to be converted.
    """
    with open("tasks.json", "w", encoding="utf-8") as file:
        json.dump({"data": segments, "predictions": []}, file)
