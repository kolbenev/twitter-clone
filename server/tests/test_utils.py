from server.database.models import User
from server.app.routes.utils import lazy_get_user_by_apikey_or_id
from server.tests.conftest import session
import pytest


# @pytest.mark.usefixtures("setup_teardown")
# async def test_get_lazy_user_api():
#     new_user = User(
#         name="michael",
#         apikey='test',
#     )
#     session.add(new_user)
#     await session.flush()
#
#     user: User = await lazy_get_user_by_apikey_or_id(user_id=new_user.id, session=session)
#     assert user.id == new_user.id