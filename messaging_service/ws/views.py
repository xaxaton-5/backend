import asyncio
import logging
from typing import Any, Dict, List, Optional

import aiohttp
from fastapi import APIRouter, Body, HTTPException, WebSocket, WebSocketDisconnect, status

from config import settings
from ws.manager import get_connection_manager


class WsMessageType:
    TEXT_MESSAGE = 'text_message'
    NOTIFICATION = 'notification'
    USER_LIST_CHANGED = 'user_list_changed'


connections_manager = get_connection_manager()
logger = logging.getLogger('messaging_service')
router = APIRouter()


@router.websocket('/ws')
async def websocket_handler(websocket: WebSocket, access_token: str) -> None:
    account_id = await get_account(access_token)
    websocket.account_id = account_id

    logger.debug('try to setup connection', extra={'ctx': {'account_id': account_id, 'token': access_token}})
    await connections_manager.connect(websocket)
    if not account_id:
        await websocket.send_json({'error': 1, 'error_message': 'account is not identified'})
        connections_manager.disconnect(websocket)
        await broadcast_user_list_changed(access_token)
        return
    await broadcast_user_list_changed(access_token)
    try:
        while True:
            command = await websocket.receive_json()
            logger.info('recieve command', command)
    except WebSocketDisconnect:
        connections_manager.disconnect(websocket)
        logger.debug('disconnected', account_id)
        await broadcast_user_list_changed(access_token)


@router.post('/notify/send')
async def notify_send(account_id: int, message: Dict[str, str]) -> Dict[str, str]:
    connection = connections_manager.active_connections.get(account_id)
    if not connection:
        return {'result': 'no-con'}

    message.update(event=WsMessageType.NOTIFICATION)
    await connection.send_json(message)
    logger.info('notification sent', extra={'ctx': {'account_id': account_id, 'msg': message}})
    return {'result': 'ok'}


@router.post('/message/send')
async def message_send(account_id: int, message: Dict[str, Any]) -> Dict[str, str]:
    current_connection = connections_manager.active_connections.get(account_id)
    if not current_connection:
        return {'result': 'no-con'}

    for _, connection in connections_manager.active_connections.items():
        message.update(event=WsMessageType.TEXT_MESSAGE)
        await connection.send_json(message)

    logger.info('message sent', extra={'ctx': {'account_id': account_id, 'msg': message}})
    return {'result': 'ok'}


def _user_detail_to_item(data: Dict[str, Any]) -> Dict[str, Any]:
    """Собирает плоский объект из ответа UserDetail (UserDetailSerializer)."""
    profile = data.get('profile') or {}
    children = profile.get('children') or []
    children_count = len(children) if isinstance(children, list) else 0
    return {
        'id': data['id'],
        'username': data['username'],
        'email': data['email'],
        'exp': profile.get('exp', data.get('total_exp', 0)),
        'is_parent': bool(profile.get('is_parent', False)),
        'children_count': children_count,
        'date_joined': data['date_joined'],
    }


def _connected_user_ids() -> List[int]:
    return sorted(uid for uid in connections_manager.active_connections.keys() if uid is not None)


async def _load_connected_users_payload(
    session: aiohttp.ClientSession,
    *,
    user_ids: List[int],
    auth_headers: Dict[str, str],
    strict: bool,
) -> List[Dict[str, Any]]:
    base = settings.CORE_URL

    async def fetch_one(user_id: int) -> Optional[Dict[str, Any]]:
        url = f'{base}/api/user/detail/{user_id}/'
        async with session.get(url, headers=auth_headers) as resp:
            if resp.status != 200:
                if strict:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f'failed to fetch user detail for id={user_id}',
                    )
                logger.warning(
                    'user detail fetch failed for broadcast',
                    extra={'ctx': {'user_id': user_id, 'status': resp.status}},
                )
                return None
            detail = await resp.json()
        return _user_detail_to_item(detail)

    items = await asyncio.gather(*[fetch_one(uid) for uid in user_ids])
    return [item for item in items if item is not None]


async def broadcast_user_list_changed(access_token: str) -> None:
    user_ids = _connected_user_ids()
    auth_headers = {'Authorization': f'Bearer {access_token}'} if access_token else {}
    message: Dict[str, Any] = {
        'event': WsMessageType.USER_LIST_CHANGED,
        'data': [],
    }
    if user_ids:
        async with aiohttp.ClientSession() as session:
            message['data'] = await _load_connected_users_payload(
                session,
                user_ids=user_ids,
                auth_headers=auth_headers,
                strict=False,
            )
    for connection in list(connections_manager.active_connections.values()):
        try:
            await connection.send_json(message)
        except Exception:
            logger.exception('failed to send user_list_changed')


@router.post('/users/list')
async def users_list(access_token: str = Body(..., embed=True)) -> List[Dict[str, Any]]:
    account_id = await get_account(access_token)
    if not account_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='account is not identified',
        )

    user_ids = _connected_user_ids()
    if not user_ids:
        return []

    auth_headers = {'Authorization': f'Bearer {access_token}'}

    async with aiohttp.ClientSession() as session:
        return await _load_connected_users_payload(
            session,
            user_ids=user_ids,
            auth_headers=auth_headers,
            strict=True,
        )


async def get_account(access_token: str) -> Optional[int]:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{settings.CORE_URL}/api/auth/', headers={'Authorization': f'Bearer {access_token}'}) as response:  # noqa: E501
            if response.status == 200:
                data = await response.json()
                return data['id']
            return None
