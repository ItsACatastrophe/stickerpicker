Serves up static files to display the element sticker picker if and only if the requester's IP address associates with an auth'd session.

2 env vars should be supplied to the container/pc running this server.
- `MATRIX_ACCESS_TOKEN`: A PAT from a user with admin access. Needed to get the active sessions.
- `DOCKER_NET_MATRIX_IP`: Really this is the protocol and host of the url for the Matrix Admin API. If you're on a loopback address this should be something like `http://127.0.0.1:8008`. Not for me but that's the general idea.

This docker image expects you to mount a volume at `web/`

This setup assumes that Gunicorn/Flask server is behind a reverse proxy. Ensure that the reverse proxy sets the `X-Real-IP` header with the requester's IP so that the correct IP address is compared against active matrix sessions.
