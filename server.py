import asyncio
import os

import aiofiles
from aiohttp import web

from fotoserver.cli import parse_arguments
from fotoserver.logging import configure_logging


async def archivate(request):
    root_photo_directory = request.app['directory']
    delay = request.app['delay']
    archive_hash = request.match_info['archive_hash']
    dir_for_archiving = os.path.join(root_photo_directory, archive_hash)
    if not os.path.exists(dir_for_archiving):
        raise web.HTTPNotFound(reason='Архив не существует или был удален')

    headers = {
        'Content-Type': 'text/html',
        'Transfer-Encoding': 'chunked',
        'Content-Disposition': f'attachment; filename="{archive_hash}.rar"'
    }
    response = web.StreamResponse()
    response.headers.update(headers)
    await response.prepare(request)

    program = 'zip'
    params = ('-qr', '-', f'{dir_for_archiving}')
    process = await asyncio.create_subprocess_exec(program, *params, stdout=asyncio.subprocess.PIPE)

    try:
        while not process.stdout.at_eof():
            logger.debug(f'Sending archive chunk {archive_hash}')
            chunk = await process.stdout.read(500000)  # 500Kb
            await response.write(chunk)
            await asyncio.sleep(delay)
    except (asyncio.CancelledError, BaseException):
        logger.debug(f'Download was interrupted {archive_hash}')
        process.terminate()
        logger.info('zip process was killed')
        raise
    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    args = parse_arguments()
    logger = configure_logging(args.no_logging)

    app = web.Application()
    app['delay'] = args.delay
    app['directory'] = args.directory
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archivate),
    ])
    web.run_app(app)
