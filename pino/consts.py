import os
import shutil

skopeo_bin = os.environ.get("SKOPEO") or shutil.which("skopeo")
umoci_bin = os.environ.get("UMOCI") or shutil.which("umoci")
