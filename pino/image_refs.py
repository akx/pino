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
