import logging
from typing import Any, Dict, Optional

import aiohttp
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from config import settings
from ws.manager import get_connection_manager


class WsMessageType:
    TEXT_MESSAGE = 'text_msg'
    NOTIFICATION = 'notification'


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
    try:
        while True:
            command = await websocket.receive_json()
            logger.info('recieve command', command)
    except WebSocketDisconnect:
        connections_manager.disconnect(websocket)
        logger.debug('disconnected', account_id)


@router.post('/notify/send')
async def notify_send(account_id: int, message: Dict[str, str]) -> Dict[str, str]:
    connection = connections_manager.active_connections.get(account_id)
    if not connection:
        return {'result': 'no-con'}

    message.update(type=WsMessageType.NOTIFICATION)
    await connection.send_json(message)
    logger.info('notification sent', extra={'ctx': {'account_id': account_id, 'msg': message}})
    return {'result': 'ok'}


@router.post('/message/send')
async def message_send(account_id: int, message: Dict[str, Any]) -> Dict[str, str]:
    current_connection = connections_manager.active_connections.get(account_id)
    if not current_connection:
        return {'result': 'no-con'}

    for receiver_id, connection in connections_manager.active_connections.items():
        if receiver_id != account_id:
            message.update(type=WsMessageType.TEXT_MESSAGE)
            await connection.send_json(message)

    logger.info('message sent', extra={'ctx': {'account_id': account_id, 'msg': message}})
    return {'result': 'ok'}


async def get_account(access_token: str) -> Optional[int]:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{settings.CORE_URL}/api/auth/', headers={'Authorization': f'Bearer {access_token}'}) as response:  # noqa: E501
            if response.status == 200:
                data = await response.json()
                return data['id']
            return None
