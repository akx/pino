import argparse
import logging
import tempfile

from pino.consts import skopeo_bin, umoci_bin
from pino.filemap import build_file_map
from pino.image_refs import qualify_image_ref
from pino.work import do_pino

log = logging.getLogger(__name__)


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

    if not umoci_bin:
        raise RuntimeError("Missing umoci tool (set UMOCI if not on PATH)")

    if not skopeo_bin:
        raise RuntimeError("Missing skopeo tool (set SKOPEO if not on PATH)")

    if not file_map:
        log.warning("No files in file map..?")

    base_image_ref = qualify_image_ref(args.base_image)
    dest_image_ref = qualify_image_ref(args.dest_image)

    with tempfile.TemporaryDirectory(prefix="pino") as work_directory:
        do_pino(
            work_directory=work_directory,
            base_image_ref=base_image_ref,
            dest_image_ref=dest_image_ref,
            file_map=file_map,
            dir_prefix=args.dir_prefix,
            dest_tag=args.dest_tag,
        )


if __name__ == "__main__":
    main()
