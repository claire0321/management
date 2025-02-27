import inspect
import json

import pytest
from asgi_lifespan import LifespanManager
from fastapi import status
from httpx import AsyncClient, ASGITransport

from app.config import TestMessageCli
from app.main import app

## Login ["/login/"]===============================

admin_credentials = {"username": "admin", "password": "admin"}
manager_credentials = {"username": "manager", "password": "manager"}
general_credentials = {"username": "general", "password": "general"}


async def get_auth_credentials(client, user):
    # async with (LifespanManager(app) as manager):
    #     async with AsyncClient(transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000") as client:
    return await client.post("/login/", data=user)


async def start_test(client, func_name: str, user: dict):
    TestMessageCli.start(func_name, len(func_name))
    auth_response = await get_auth_credentials(client, user)
    auth_token = json.loads(auth_response.content.decode())["access_token"]
    return {"authorization": auth_token}


class TestLogin:
    @pytest.mark.asyncio
    async def test_admin_login(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                TestMessageCli.start(func_name, len(func_name))
                response = await get_auth_credentials(client, admin_credentials)
                assert response.status_code == 200
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_admin_login_wrong_username(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                TestMessageCli.start(func_name, len(func_name))
                response = await client.post("/login/", data={"username": "admins", "password": "admin"})
                assert response.status_code == 401
                assert response.json() == {"ERROR": "UNAUTHORIZED"}
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_admin_login_wrong_password(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                TestMessageCli.start(func_name, len(func_name))
                response = await client.post("/login/", data={"username": "admin", "password": "admins"})
                assert response.status_code == 401
                assert response.json() == {"ERROR": "Incorrect password"}
                TestMessageCli.finish(func_name, len(func_name))


## ================================================================
## -------------------------- USER --------------------------------
## ================================================================


class TestUserAdmin:
    username: str = "NewUser"

    @pytest.mark.asyncio
    async def test_create_user_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                try:
                    func_name = inspect.currentframe().f_code.co_name
                    auth_header = await start_test(client, func_name, admin_credentials)

                    new_user = {"username": self.username, "password": self.username}
                    response = await client.post("/users/", json=new_user, headers=auth_header)
                    print(response.json())
                    if response.json() == {"ERROR": f"Username '{self.username}' already exists"}:
                        await self.test_delete_user_by_admin()
                        response = await client.post("/users/", json=new_user, headers=auth_header)
                    assert response.status_code == 201
                    assert response.json() == {"username": self.username, "email": None}
                    TestMessageCli.finish(func_name, len(func_name))
                finally:
                    await client.delete()

    @pytest.mark.asyncio
    async def test_create_user_already_exist_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                new_user = {"username": self.username, "password": self.username}
                response = await client.post("/users/", json=new_user, headers=auth_header)
                assert response.status_code == status.HTTP_409_CONFLICT
                assert response.json() == {"ERROR": f"Username '{self.username}' already exists"}
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_create_user_without_username_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                new_user = {"password": self.username}
                response = await client.post("/users/", json=new_user, headers=auth_header)
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
                assert response.json() == {"ERROR": "Field 'username' is missing or required."}
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_create_user_username_not_alnum_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                new_user = {"username": f"{self.username}_", "password": self.username}
                response = await client.post("/users/", json=new_user, headers=auth_header)
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
                assert response.json() == {"ERROR": "Username should be alphanum."}
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_create_user_without_password_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                new_user = {"username": self.username, "email": f"{self.username}@example.com"}
                response = await client.post("/users/", json=new_user, headers=auth_header)
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
                assert response.json() == {"ERROR": "Field 'password' is missing or required."}
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_create_user_empty_password_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                new_user = {"username": self.username, "password": "    "}
                response = await client.post("/users/", json=new_user, headers=auth_header)
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
                assert response.json() == {"ERROR": "password cannot be empty"}
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_create_user_with_space_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                new_user = {"username": self.username, "password": "asdf  asdfa"}
                response = await client.post("/users/", json=new_user, headers=auth_header)
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
                assert response.json() == {
                    "ERROR": "Validation Error. Please provide value without any space in password."}
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_delete_user_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                response = await client.delete(f"/users/delete?username={self.username}", headers=auth_header)
                assert response.status_code == 200
                assert response.json() == {"message": f"User '{self.username}' deleted successfully"}
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_get_users_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                response = await client.get("/users/", headers=auth_header)
                assert response.status_code == 200
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_get_user_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                response = await client.get("/users/admin", headers=auth_header)
                assert response.status_code == 200
                print(response.json())
                assert response.json() == {"username": "admin", "email": "admin@example.com", "role_id": 1}
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_update_user_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                update_user = {"username": self.username, "email": f"{self.username}@example.com"}
                response = await client.put("/users/update/", json=update_user, headers=auth_header)
                if response.json() == {"ERROR": f"{self.username} not found"}:
                    await self.test_create_user_by_admin()
                    response = await client.put("/users/update/", json=update_user, headers=auth_header)
                print(response.json())
                assert response.status_code == 200
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_activate_user_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                response = await client.put(f"/users/activate?username={self.username}", headers=auth_header)
                print(response.json())
                assert response.status_code == 200
                assert response.json() == {
                    "username": self.username,
                    "email": "NewUser@example.com",
                    "role_id": 3,
                }
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_deactivate_user_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                response = await client.put("/users/deactivate?username=NewUser", headers=auth_header)
                await self.test_activate_user_by_admin()
                print(response.json())
                assert response.status_code == 200
                assert response.json() == {"message": f"User '{self.username}' is deactivated"}
                TestMessageCli.finish(func_name, len(func_name))


class TestUserManager:
    username: str = "NewUser"

    @pytest.mark.asyncio
    async def test_create_user_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                new_user = {"username": self.username, "password": self.username}
                response = await client.post("/users/", json=new_user, headers=auth_header)
                print(response.json())
                if response.json() == {"ERROR": f"Username '{self.username}' already exists"}:
                    await self.test_delete_user_by_admin()
                    response = await client.post("/users/", json=new_user, headers=auth_header)
                assert response.status_code == 201
                assert response.json() == {"username": self.username, "email": None}
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_create_user_already_exist_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                new_user = {"username": self.username, "password": self.username}
                response = await client.post("/users/", json=new_user, headers=auth_header)
                assert response.status_code == status.HTTP_409_CONFLICT
                assert response.json() == {"ERROR": f"Username '{self.username}' already exists"}
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_create_user_without_username_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                new_user = {"password": self.username}
                response = await client.post("/users/", json=new_user, headers=auth_header)
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
                assert response.json() == {"ERROR": "Field 'username' is missing or required."}
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_create_user_username_not_alnum_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                new_user = {"username": f"{self.username}_", "password": self.username}
                response = await client.post("/users/", json=new_user, headers=auth_header)
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
                assert response.json() == {"ERROR": "Username should be alphanum."}
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_create_user_without_password_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                new_user = {"username": self.username, "email": f"{self.username}@example.com"}
                response = await client.post("/users/", json=new_user, headers=auth_header)
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
                assert response.json() == {"ERROR": "Field 'password' is missing or required."}
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_create_user_empty_password_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                new_user = {"username": self.username, "password": "    "}
                response = await client.post("/users/", json=new_user, headers=auth_header)
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
                assert response.json() == {"ERROR": "password cannot be empty"}
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_create_user_with_space_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                new_user = {"username": self.username, "password": "asdf  asdfa"}
                response = await client.post("/users/", json=new_user, headers=auth_header)
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
                assert response.json() == {
                    "ERROR": "Validation Error. Please provide value without any space in password."}
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_delete_user_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                response = await client.delete(f"/users/delete?username={self.username}", headers=auth_header)
                assert response.status_code == 200
                assert response.json() == {"message": f"User '{self.username}' deleted successfully"}
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_get_users_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                response = await client.get("/users/", headers=auth_header)
                assert response.status_code == 200
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_get_user_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                response = await client.get("/users/admin", headers=auth_header)
                assert response.status_code == 200
                print(response.json())
                assert response.json() == {"username": "admin", "email": "admin@example.com", "role_id": 1}
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_update_user_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                update_user = {"username": self.username, "email": f"{self.username}@example.com"}
                response = await client.put("/users/update/", json=update_user, headers=auth_header)
                if response.json() == {"ERROR": f"{self.username} not found"}:
                    await self.test_create_user_by_admin()
                    response = await client.put("/users/update/", json=update_user, headers=auth_header)
                print(response.json())
                assert response.status_code == 200
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_activate_user_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                response = await client.put(f"/users/activate?username={self.username}", headers=auth_header)
                print(response.json())
                assert response.status_code == 200
                assert response.json() == {
                    "username": self.username,
                    "email": "NewUser@example.com",
                    "role_id": 3,
                }
                TestMessageCli.finish(func_name, len(func_name))

    @pytest.mark.asyncio
    async def test_deactivate_user_by_admin(self):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                    transport=ASGITransport(app=manager.app), base_url="http://127.0.0.1:8000"
            ) as client:
                func_name = inspect.currentframe().f_code.co_name
                auth_header = await start_test(client, func_name, admin_credentials)

                response = await client.put("/users/deactivate?username=NewUser", headers=auth_header)
                await self.test_activate_user_by_admin()
                print(response.json())
                assert response.status_code == 200
                assert response.json() == {"message": f"User '{self.username}' is deactivated"}
                TestMessageCli.finish(func_name, len(func_name))
# TestMessageCli.start(func_name, len(func_name))
# TestMessageCli.finish(func_name, len(func_name))
