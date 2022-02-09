# pino

Stack files into a container image.

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

## Caveats

- Pino currently requires quite some additional disk space.
- UIDs are not mapped. Unless your local user's UID is the one you want in the container, it's not going to be correct.

## What's with the name?

`pino` is Finnish for "stack", and that's what this does.
