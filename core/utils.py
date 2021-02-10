import os
import inspect
import socket

from datetime import datetime

import dhooks
from discord import Color, Embed


async def log_server_start(app):
    embed = Embed(color=Color.green(), timestamp=datetime.utcnow())
    if os.environ["MATAXAPI_DOMAIN"] == "localhost":
        url = f'http://{os.environ["MATAXAPI_DOMAIN"]}:{os.environ["MATAXAPI_PORT"]}'
    else:
        url = f'https://{os.environ["MATAXAPI_DOMAIN"]}'
    embed.set_author(name='[INFO] Starting Worker', url=url)
    if url:
        embed.add_field(name='Live at', value=url)
        embed.add_field(name='Github', value='[matrix2113/matax-api](https://github.com/matrix2113/matax-api)')

    embed.set_footer(text=f'Hostname: {socket.gethostname()}')
    return await app.webhook.send(embeds=[embed])


async def log_server_stop(app):
    embed = Embed(color=Color.red(), timestamp=datetime.utcnow())
    embed.set_author(name='[INFO] Stopping Worker')
    embed.set_footer(text=f'Hostname: {socket.gethostname()}')
    return await app.webhook.send(embeds=[embed])


async def log_server_update(app):
    embed = Embed(color=Color.orange, timestamp=datetime.utcnow())
    embed.set_footer(text=f'Hostname: {socket.gethostname()}')
    embed.set_author(name='[INFO] Server updating and restarting.')
    return await app.webhook.send(embeds=[embed])


async def log_server_error(app, request, excstr):
    embed = Embed(color=Color.red, timestamp=datetime.utcnow())
    embed.set_author(name='[ERROR] Exception occured on server}')
    embed.description = f'{request.url}\n```py\n{excstr}```'
    embed.set_footer(text=f'Hostname: {socket.gethostname()}')
    return await app.webhook.send(embeds=[embed])


async def log_message(app, message):
    embed = Embed(color=Color.orange, timestamp=datetime.utcnow())
    embed.set_author(name='[INFO] Message')
    embed.description = f'```\n{message}```'
    embed.set_footer(text=f'Hostname: {socket.gethostname()}')
    return await app.webhook.send(embeds=[embed])


def get_stack_variable(name):
    stack = inspect.stack()
    try:
        for frames in stack:
            try:
                frame = frames[0]
                current_locals = frame.f_locals
                if name in current_locals:
                    return current_locals[name]
            finally:
                del frame
    finally:
        del stack
