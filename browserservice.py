"""
Very simple example of a Headless Browser Like a Service

aiohttp API and Pyppeteer

Example using Scrapy shell:

import json
from scrapy import Request

headers = {'Content-Type': 'application/json'}
params = {'url': 'https://www.nytimes.com/'}

fetch(Request('http://127.0.0.1:8080/goto', method='POST', headers=headers, body=json.dumps(params)))

response_data = json.loads(response.body)

"""

import sys
import logging
import asyncio
import argparse
from aiohttp import web
from pyppeteerbrowser import Browser


LOGFORMAT = '%(levelname)s: %(asctime)s %(filename)s: %(message)s'


parser = argparse.ArgumentParser(description="Pyppeteer API: aiohttp server")
parser.add_argument('--path')
parser.add_argument('--port')


def is_empty(value):
    '''Check if value is empty: very simple!!'''
    if not value:
        return True
    value = str(value).strip()
    return not value


def validate_parameters(params: dict, errors: list):
    '''Validate the JSON parameters'''
    if 'url' not in params:
        errors.append('You must to specify an URL')
    elif is_empty(params['url']):
        errors.append('The URL must not be empty')


async def get_page_url(browser, url, timeout=30):
    '''Go to a page URL'''
    json_response = None
    try:
        response = await browser.page.goto(url, timeout=timeout*1000)  # Pyppeteer uses miliseconds
    except asyncio.TimeoutError:
        json_response = web.json_response({'message': 'Timeout error',
                                           'data': {'url': url,
                                                    'body': '',
                                                    'headers': {}}},
                                          status=504)
    except Exception as excp:  # pylint: disable=broad-except
        json_response = web.json_response({'message': 'Exception found',
                                           'data': {'url': url,
                                                    'body': '{!r}'.format(excp),
                                                    'headers': {}}},
                                          status=500)
    else:
        try:
            body = await response.text()
        except:  # pylint: disable=bare-except
            body = ''
        message = 'All OK' if response.ok else 'An error has occurred'
        json_response = web.json_response({'message': message,
                                           'data': {'url': response.url,
                                                    'body': body,
                                                    'headers': response.headers}},
                                          status=response.status)
    return json_response


async def goto_handler(request):
    '''Handler for a given URL request'''
    params = await request.json()
    errors = []
    validate_parameters(params, errors)
    if errors:
        return web.json_response({'message': 'Validation Error',
                                  'data': {},
                                  'errors': errors},
                                 status=400)
    json_resp = web.json_response({'message': 'Empty', 'data': {}}, status=404)
    async with Browser(binary='default') as browser:
        json_resp = await get_page_url(browser, params['url'])
    return json_resp


async def make_app():
    '''Make the main app and return it'''
    routes = [
        web.post('/goto', goto_handler),
    ]

    web_app = web.Application()
    web_app.add_routes(routes)

    return web_app


if __name__ == '__main__':
    main_loop = asyncio.get_event_loop()
    app_future = make_app()

    app = main_loop.run_until_complete(app_future)

    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format=LOGFORMAT, datefmt='%Y-%m-%d %H:%M:%S')

    web.run_app(app, path=args.path, port=args.port)
