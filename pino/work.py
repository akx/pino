import datetime
import logging
import os
import platform
import shutil
from typing import List, Optional

from pino.consts import skopeo_bin, umoci_bin
from pino.filemap import FileMap
from pino.utils import check_call_verbose

log = logging.getLogger(__name__)


def do_pino(
    *,
    work_directory: str,
    base_image_ref: str,
    dest_image_ref: str,
    file_map: FileMap,
    dir_prefix="/",
    dest_tag: Optional[str] = None,
    update_image_mtime: bool = True,
) -> None:
    skopeo_args = build_skopeo_args()
    image_dir = os.path.join(work_directory, "image")
    oci_ref = f"{image_dir}:1"
    check_call_verbose(skopeo_args + ["copy", base_image_ref, f"oci:{oci_ref}"])
    inject_files(
        oci_ref=oci_ref,
        overlay_dir=os.path.join(work_directory, "overlay"),
        file_map=file_map,
        dir_prefix=dir_prefix,
    )
    if update_image_mtime:
        timestamp = f"{datetime.datetime.utcnow().isoformat(timespec='seconds')}+00:00"
        check_call_verbose(
            [umoci_bin, "config", "--image", oci_ref, f"--created={timestamp}"]
        )
    skopeo_cmd = skopeo_args + ["copy", f"oci:{oci_ref}", dest_image_ref]
    if dest_tag:
        skopeo_cmd.extend(["--additional-tag", dest_tag])
    check_call_verbose(skopeo_cmd)


def build_skopeo_args() -> List[str]:
    skopeo_args = [skopeo_bin]
    # There are no macOS containers, so assume user wants Linux
    if platform.system() == "Darwin":
        skopeo_args.append("--override-os=linux")
    return skopeo_args


def inject_files(
    *, oci_ref: str, overlay_dir: str, file_map: FileMap, dir_prefix: str
) -> None:
    if not file_map:
        return
    for dst_part_path, src_path in file_map.items():
        dst_path = os.path.join(overlay_dir, dst_part_path)
        dst_dir = os.path.dirname(dst_path)
        os.makedirs(dst_dir, exist_ok=True)
        print(f"Copying {src_path} -> {dst_path}...")
        shutil.copyfile(src_path, dst_path)
    # TODO: should support uid map here
    check_call_verbose(
        [umoci_bin, "insert", "--image", oci_ref, overlay_dir, dir_prefix]
    )
