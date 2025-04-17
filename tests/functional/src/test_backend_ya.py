import datetime as dt
import http

import aiohttp
import pytest

from tests.functional.settings import test_settings


# @pytest.mark.asyncio
# async def test_yandex_msisdn(sqlite_conn_1, create_table_yandex):
#     """Поиск по точному номеру телефона"""
#     await create_table_yandex()

#     async with sqlite_conn_1.execute('SELECT * FROM yandex_eda WHERE id=1;') as cursor:
#         id, phone_number, yandex_name, yandex_created_at, yandex_place_id, yandex_place_name, yandex_address_city, yandex_address_street, yandex_address_house, yandex_address_office, yandex_address_comment, yandex_region_id, yandex_amount_rub, yandex_sum_orders = await cursor.fetchone()  # ignore

#     async with aiohttp.ClientSession() as session:
#         async with session.post(
#             f'http://{test_settings.host}:{test_settings.port}/api/yandex/msisdn',
#             json={'phone_number': phone_number}
#         ) as response:
#             assert response.status == http.HTTPStatus.OK
#             result = await response.json()
#             assert len(result) >= 1
#             assert result[0].get('id') == id
#             assert dt.datetime.fromisoformat(result[0].get('yandex_created_at')).strftime('%Y-%m-%d') == yandex_created_at  # ignore


#         async with session.post(
#             f'http://{test_settings.host}:{test_settings.port}/api/yandex/msisdn',
#             json={'phone_number': phone_number + 1}
#         ) as response:
#             assert response.status == http.HTTPStatus.OK
#             result = await response.json()
#             assert len(result) == 0


# @pytest.mark.asyncio
# async def test_yandex_msisdn_like(sqlite_conn_1, create_table_yandex):
#     """Поиск по примерному номеру телефона"""

#     await create_table_yandex()

#     async with sqlite_conn_1.execute('SELECT * FROM yandex_eda WHERE id=2;') as cursor:
#         id, phone_number, yandex_name, yandex_created_at, yandex_place_id, yandex_place_name, yandex_address_city, yandex_address_street, yandex_address_house, yandex_address_office, yandex_address_comment, yandex_region_id, yandex_amount_rub, yandex_sum_orders = await cursor.fetchone()  # ignore

#     async with aiohttp.ClientSession() as session:
#         like_phone_number = int(str(phone_number)[1:-1])
#         async with session.post(
#             f'http://{test_settings.host}:{test_settings.port}/api/yandex/msisdn/like',
#             json={'phone_number': like_phone_number}
#         ) as response:
#             assert response.status == http.HTTPStatus.OK
#             result = await response.json()
#             assert len(result) >= 1
#             assert result[0].get('id') == id
#             assert result[0].get('phone_number') == phone_number
#             assert dt.datetime.fromisoformat(result[0].get('yandex_created_at')).strftime('%Y-%m-%d') == yandex_created_at  # ignore

#         async with session.post(
#             f'http://{test_settings.host}:{test_settings.port}/api/yandex/msisdn/like',
#             json={'phone_number': like_phone_number + 1}
#         ) as response:
#             assert response.status == http.HTTPStatus.OK
#             result = await response.json()
#             assert len(result) == 0
