import pathlib
import flask
import requests
import os

ips_with_sessions = []

class SessionSecuredStaticFlask(flask.Flask):
    def send_static_file(self, filename):
        if flask.request.remote_addr in ips_with_sessions:
            return super(SessionSecuredStaticFlask, self).send_static_file(filename)

        # If an IP isn't authed it COULD be a new session. Refresh session list.
        # TODO: can probably make this request without hitting the internet. Over the docker network?
        response = requests.get(
            #url=f"https://matrix.catscodecorner.com/_synapse/admin/v2/users?from=0&limit=10&guests=false",
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

        # Note: Simulates the user's IP being authed to a session
        ips_with_sessions.append(flask.request.remote_addr)

        if flask.request.remote_addr in ips_with_sessions:
            return super(SessionSecuredStaticFlask, self).send_static_file(filename)

        return "<p>You're not auth'd, sorry!</p>"

app = SessionSecuredStaticFlask(__name__, static_url_path="", static_folder=f"{pathlib.Path(__file__).parent.resolve()}/web")

@app.route("/web")
def web():
    return app.send_static_file("index.html")


if __name__ == "__main__":
    app.run()
