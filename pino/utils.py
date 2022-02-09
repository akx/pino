import logging
import shlex
import subprocess

log = logging.getLogger(__name__)


def check_call_verbose(args) -> None:
    log.info("`%s`", shlex.join(args))
    subprocess.check_call(args)
