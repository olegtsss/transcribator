import pytest_asyncio

from tests.functional.settings import test_settings
from tests.functional.utils import (generate_digits, generate_name,
                                    generate_username)


# @pytest_asyncio.fixture(name='rabbit_conn')
# async def sqlite_conn_1():
#     sqlite_conn = await aiosqlite.connect(test_settings.database_1_name)
#     yield sqlite_conn
#     await sqlite_conn.close()



# @pytest_asyncio.fixture(name='create_table_yandex')
# def create_table_yandex(sqlite_conn_1: Connection):
#     async def inner():
#         fake = Faker()
#         await sqlite_conn_1.execute('DROP TABLE IF EXISTS yandex_eda;')
#         await sqlite_conn_1.commit()

#     return inner
