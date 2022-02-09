# pino

Stack files into a container image (without a running Docker daemon, too)

## Standing on the shoulders of giants

This project is really just a thin wrapper around

- [Skopeo](https://github.com/containers/skopeo) for extracting and manipulating Docker and OCI images
- [Umoci](https://github.com/opencontainers/umoci) for manipulating OCI images

## Requirements

- Python 3.6+
- Skopeo and Umoci

## Usage example

- Start from a `python:3.10` image available to your local Docker daemon,
- Add a layer containing the local `./tests/app` directory as `/app`
- Save the result as `appified-python.tar` with an embedded tag `appified-python:latest` (which can be `docker load`ed):

```
python3 pino.py --base-image python:3.10 --dest-image ./appified-python.tar --add ./tests/app:/app --dest-tag appified-python:latest
```

The same, but directly to the local Docker daemon:

```
python3 pino.py --base-image python:3.10 --dest-image appified-python:latest --add ./tests/app:/app
```

### Look ma, no Docker

How about without Docker running at all?! This grabs Python 3.10 from docker.io, applies our changes and saves a tarball.

```
python3 pino.py --base-image docker://docker.io/python:3.10 --dest-image appified-python.tar --add ./tests/app:/app
```

Since pino uses Skopeo under the hood, you can follow [Skopeo's authentication](https://github.com/containers/skopeo#authenticating-to-a-registry) instructions, then directly `--dest-image docker://myregistry.local:5000/` too.

## Caveats

- Pino currently requires quite some additional disk space.
- UIDs are not mapped. Unless your local user's UID is the one you want in the container, it's not going to be correct.

## What's with the name?

`pino` is Finnish for "stack", and that's what this does.
