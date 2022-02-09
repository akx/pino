import argparse
import datetime
import logging
import os
import shlex
import shutil
import subprocess
import tempfile
from typing import List, Dict, Optional

skopeo = os.environ.get("SKOPEO") or shutil.which("skopeo")
umoci = os.environ.get("UMOCI") or shutil.which("umoci")
log = logging.getLogger(__name__)


def check_call_verbose(args) -> None:
    log.info("`%s`", shlex.join(args))
    subprocess.check_call(args)


def do_pino(
    base_image_ref: str,
    dest_image_ref: str,
    file_map: Dict[str, str],
    dir_prefix="/",
    dest_tag: Optional[str] = None,
    update_image_mtime: bool = True,
) -> None:
    with tempfile.TemporaryDirectory(prefix="pino") as tmpdir:
        image_dir = os.path.join(tmpdir, "image")
        oci_ref = f"{image_dir}:1"
        check_call_verbose([skopeo, "copy", base_image_ref, f"oci:{oci_ref}"])
        overlay_dir = os.path.join(tmpdir, "overlay")
        for dst_part_path, src_path in file_map.items():
            dst_path = os.path.join(overlay_dir, dst_part_path)
            dst_dir = os.path.dirname(dst_path)
            os.makedirs(dst_dir, exist_ok=True)
            print(f"Copying {src_path} -> {dst_path}...")
            shutil.copyfile(src_path, dst_path)
        # TODO: should support uid map here
        check_call_verbose(
            [umoci, "insert", "--image", oci_ref, overlay_dir, dir_prefix]
        )
        if update_image_mtime:
            timestamp = (
                f"{datetime.datetime.utcnow().isoformat(timespec='seconds')}+00:00"
            )
            check_call_verbose(
                [umoci, "config", "--image", oci_ref, f"--created={timestamp}"]
            )
        skopeo_cmd = [skopeo, "copy", f"oci:{oci_ref}", dest_image_ref]
        if dest_tag:
            skopeo_cmd.extend(["--additional-tag", dest_tag])
        check_call_verbose(skopeo_cmd)


def build_file_map(file_atoms: List[str]) -> Dict[str, str]:
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


KNOWN_SKOPEO_TRANSPORTS = {
    "containers-storage",
    "dir",
    "docker",
    "docker-archive",
    "docker-daemon",
    "oci",
    "oci-archive",
    "ostree",
    "sif",
    "tarball",
}


def qualify_image_ref(image_ref: str) -> str:
    # If the image smells like a Skopeo-transport-prefixed thing, assume the user knows what they're doing
    if any(
        image_ref.startswith(f"{transport}:") for transport in KNOWN_SKOPEO_TRANSPORTS
    ):
        return image_ref
    # If it ends with a .tar, assume the user means a local Docker tarball
    if image_ref.endswith(".tar"):
        return f"docker-archive:{image_ref}"
    # Otherwise, assume it's a local docker image
    return f"docker-daemon:{image_ref}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-image", required=True)
    ap.add_argument("--dest-image", required=True)
    ap.add_argument("--dest-tag")
    ap.add_argument("--dir-prefix", default="/")
    ap.add_argument("--add", dest="files", action="append", default=[])
    args = ap.parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s:%(asctime)s] %(message)s",
    )

    file_map = build_file_map(args.files)

    if not umoci:
        raise RuntimeError("Missing umoci tool (set UMOCI if not on PATH)")

    if not skopeo:
        raise RuntimeError("Missing skopeo tool (set SKOPEO if not on PATH)")

    if not file_map:
        raise RuntimeError("No files to add, nothing to do")

    base_image_ref = qualify_image_ref(args.base_image)
    dest_image_ref = qualify_image_ref(args.dest_image)
    do_pino(
        base_image_ref,
        dest_image_ref,
        file_map,
        dir_prefix=args.dir_prefix,
        dest_tag=args.dest_tag,
    )


if __name__ == "__main__":
    main()
