import requests

API_URL = "http://localhost:8000"


def register_user(email, password):
    response = requests.post(
        f"{API_URL}/auth/register",
        json={
            "email": email,
            "password": password
        }
    )

    return response


def login_user(email, password):
    response = requests.post(
        f"{API_URL}/auth/jwt/login",
        data={
            "username": email,
            "password": password
        }
    )

    return response


def get_feed(token):
    response = requests.get(
        f"{API_URL}/feed",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    return response


def upload_post(token, uploaded_file, caption):
    response = requests.post(
        f"{API_URL}/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type
            )
        },
        data={
            "caption": caption
        }
    )

    return response


def delete_post(token, post_id):
    response = requests.delete(
        f"{API_URL}/posts/{post_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    return response