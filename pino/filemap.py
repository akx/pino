import logging
import os
from typing import Dict, List

log = logging.getLogger(__name__)

FileMap = Dict[str, str]


def build_file_map(file_atoms: List[str]) -> FileMap:
    file_map = {}
    for atom in file_atoms:
        src, _, dst = atom.partition(":")
        if not dst:
            raise ValueError(f"Invalid destination {dst}")
        dst = os.path.relpath(dst, "/")
        if os.path.isdir(src):
            for dirpath, dirnames, filenames in os.walk(src):
                # TODO: here would be a great point to add filters for filenames
                for filename in filenames:
                    dst_filename = os.path.normpath(
                        os.path.join(dst, os.path.relpath(dirpath, src), filename)
                    )
                    src_filename = os.path.normpath(os.path.join(dirpath, filename))
                    if os.path.isfile(src_filename):
                        file_map[dst_filename] = src_filename
        elif os.path.isfile(src):
            file_map[dst] = src
        else:
            raise RuntimeError(f"{src}: not a directory or file")
    return file_map
