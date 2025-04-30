from service.common import status


def test_415_unsupported_media_type(client):
    """Trigger 415 Unsupported Media Type"""

    @client.application.route("/recommendations", methods=["POST"])
    def dummy_post():
        from flask import request

        if request.content_type != "application/json":
            return "Unsupported Media Type", status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        return "OK", 200

    response = client.post(
        "/recommendations", data="bad data", content_type="text/plain"
    )
    assert response.status_code == 415
    assert "Unsupported Media Type" in response.get_data(as_text=True)


def test_500_internal_server_error(client):
    """Trigger 500 Internal Server Error"""

    @client.application.route("/trigger500")
    def broken():
        raise Exception("boom")

    response = client.get("/trigger500")
    assert response.status_code == 500
    assert "Internal Server Error" in response.get_data(as_text=True)
