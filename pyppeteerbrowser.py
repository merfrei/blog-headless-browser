"""
Browser

It emulates a browser using Pyppeteer with Chromium
"""

import logging
from pyppeteer import launch


VIEWPORT = '1920x1080'
USER_AGENT = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/81.0.4044.129 Safari/537.36')


class BrowserError(Exception):
    '''A Browser Exception'''


class Browser:
    """Wrap a Pyppeteer instance"""

    def __init__(self, binary: str):
        '''
        @params binary: the path to the Chrome/Chromium binary (you can use `default`)
        '''
        self.binary = binary
        self.args = ['--no-sandbox', '--start-fullscreen']
        self.browser = None
        self.page = None

    async def __aenter__(self):
        '''To use into a with statement'''
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        '''Run after the Browser is used'''
        if exc_type is not None:
            logging.error('An error ocurred: %r : %r : %r', exc_type, exc_value, traceback)
        await self.finish()

    async def start(self):
        '''Start the browser'''
        args = list(self.args)
        if self.binary == 'default':
            self.browser = await launch(args=args, ignoreHTTPSErrors=True)
        else:
            try:
                self.browser = await launch(args=args, executablePath=self.binary,
                                            ignoreHTTPSErrors=True)
            except OSError:
                raise BrowserError('Binary not found: {}'.format(self.binary))
        self.page = await self.browser.newPage()
        await self.set_viewport(self.page, VIEWPORT)
        await self.page.setUserAgent(USER_AGENT)

    async def finish(self):
        '''Stop the browser'''
        await self.browser.close()

    @staticmethod
    async def set_viewport(page, viewport):
        '''Set the viewport on the page
        @param viewport: str (<width>x<height>)'''
        vp_w, vp_h = viewport.split('x')
        await page.setViewport({'width': int(vp_w), 'height': int(vp_h)})
