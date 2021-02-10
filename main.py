import datetime
import os
import socket
import traceback

import aiohttp
import dhooks

from motor.motor_asyncio import AsyncIOMotorClient
from jinja2 import Environment, PackageLoader

from sanic import Sanic, response
from sanic.exceptions import SanicException
from sanic_session import Session, InMemorySessionInterface

from core import utils

app = Sanic(__name__)
Session(app, interface=InMemorySessionInterface(domain=os.environ["MATAXAPI_DOMAIN"]))

app.static('/static', './static')

app.static('/favicon.ico', './static/favicon.ico')

jinja_env = Environment(loader=PackageLoader('main', 'templates'))


def render_template(name, *args, **kwargs):
    template = jinja_env.get_template(name + '.html')
    request = utils.get_stack_variable('request')
    kwargs['request'] = request
    kwargs['session'] = request['session']
    kwargs['user'] = request['session'].get('user')

    kwargs.update(globals())

    return response.html(template.render(*args, **kwargs))


app.render_template = render_template


@app.listener('before_server_start')
async def start(app, loop):
    hook = f'https://discord.com/api/webhooks/{os.environ["MATAXAPI_WEBHOOKID"]}/{os.environ["MATAXAPI_WEBHOOKTOKEN"]}'
    app.session = aiohttp.ClientSession(loop=loop)
    app.webhook = dhooks.Webhook.Async(url=hook)
    app.webhook.username = 'api.matax.dev'

    await utils.log_server_start(app)


@app.listener('after_server_stop')
async def api_close(app, loop):
    await utils.log_server_stop(app)
    await app.session.close()


@app.exception(SanicException)
async def api_exception(request, exception):
    resp = {
        'success': False,
        'error': str(exception)
    }

    print(exception)

    return response.json(resp, status=exception.status_code)


@app.exception(Exception)
async def api_error(request, exception):
    resp = {
        'success': False,
        'error': str(exception)
    }

    try:
        raise exception
    except:
        exc = traceback.format_exc()
        print(exc)

    if len(exc) > 1000:
        exc = exc[:1000]

    em = dhooks.Embed(color=0xe74c3c, title=f'`[ERROR] - {request.method} {request.url}`')
    em.description = f'```py\n{exec}```'
    em.set_footer(f'Host: {socket.gethostname()} | Domain: {os.environ["MATAXAPI_DOMAIN"]}')

    app.add_task(app.webhook.send(embeds=[em]))

    return response.json(resp, status=500)

@app.get('/')
async def index(request):
    return render_template(
        'index',
        title='Matax API',
        message='Currently in development'
    )

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.environ["MATAXAPI_PORT"]))