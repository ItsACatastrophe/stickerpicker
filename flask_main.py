import flask
import logging
import os
import pathlib
import requests

ips_with_sessions = []

class SessionSecuredStaticFlask(flask.Flask):
    def send_static_file(self, filename):
        requester_ip = flask.request.headers.get("X-Real-IP")

        if requester_ip in ips_with_sessions:
            app.logger.debug(f"{requester_ip} found in IPs with sessions. No refresh needed.")
            return super(SessionSecuredStaticFlask, self).send_static_file(filename)

        # If an IP isn't authed it COULD be a new session. Refresh session list.
        response = requests.get(
            url=f"{os.getenv("DOCKER_NET_MATRIX_IP")}/_synapse/admin/v2/users?from=0&limit=10&guests=false",
            headers={
                "Authorization": f"Bearer {os.getenv("MATRIX_ACCESS_TOKEN")}"
            }
        )

        # A name is an ID for some reason
        user_ids = [user["name"] for user in response.json()["users"]]

        for user_id in user_ids:
            response = requests.get(
                url=f"{os.getenv("DOCKER_NET_MATRIX_IP")}/_synapse/admin/v1/whois/{user_id}",
                headers={
                    "Authorization": f"Bearer {os.getenv("MATRIX_ACCESS_TOKEN")}"
                }
            )

            # Currently devices aren't named, they're just empty strings. Why...
            for session in response.json()["devices"][""]["sessions"]:
                for connection in session["connections"]:
                    ips_with_sessions.append(connection["ip"])

        if requester_ip in ips_with_sessions:
            app.logger.debug(f"{requester_ip} found in IPs with sessions after refresh.")
            app.logger.debug(f"IPs with session after refresh: {ips_with_sessions}")
            return super(SessionSecuredStaticFlask, self).send_static_file(filename)

        return "<p>You're not auth'd, sorry!</p>"

app = SessionSecuredStaticFlask(__name__, static_url_path="", static_folder=f"{pathlib.Path(__file__).parent.resolve()}/web")

@app.route("/web")
def web():
    app.logger.debug(f"IPs with session: {ips_with_sessions}")
    return app.send_static_file("index.html")


if __name__ == "__main__":
    app.run()

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
