import asyncio
import datetime
import os

import aiofiles
from aiohttp import web
from dotenv import load_dotenv

from fotoserver.cli import parse_arguments
from fotoserver.logging import configure_logging

load_dotenv()
args = parse_arguments()
logger = configure_logging(args.no_logging)


async def uptime_handler(request):
    response = web.StreamResponse()

    # Большинство браузеров не отрисовывают частично загруженный контент, только если это не HTML.
    # Поэтому отправляем клиенту именно HTML, указываем это в Content-Type.
    response.headers['Content-Type'] = 'text/html'

    # Отправляет клиенту HTTP заголовки
    await response.prepare(request)
    while True:
        formatted_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f'{formatted_date}<br>'  # <br> — HTML тег переноса строки
        # Отправляет клиенту очередную порцию ответа
        await response.write(message.encode('utf-8'))
        await asyncio.sleep(args.delay)


def write_to_file(data, name='EgrassaZip'):
    file_path = os.path.join(os.getcwd(), name)
    with open(file_path, 'ab') as f:
        f.write(data)


async def archivate(request):
    hash = request.match_info.get('archive_hash')
    file_path = os.path.join(args.directory, hash)
    if not os.path.exists(file_path):
        raise web.HTTPNotFound(reason='Архив не существует или был удален')

    response = web.StreamResponse()
    response.headers['Content-Type'] = 'text/html'
    response.headers['Transfer-Encoding'] = 'chunked'
    response.headers['Content-Disposition'] = f'attachment; filename="{hash}.rar"'
    await response.prepare(request)

    program = 'zip'
    params = ('-jqr', '-', f'{file_path}')
    process = await asyncio.create_subprocess_exec(program, *params, stdout=asyncio.subprocess.PIPE)

    try:
        while not process.stdout.at_eof():
            logger.debug(f'Sending archive chunk {hash}')
            chunk = await process.stdout.read(500000)  # 500Kb
            await response.write(chunk)
            await asyncio.sleep(args.delay)
    except (asyncio.CancelledError, BaseException):
        logger.debug(f'Download was interrupted {hash}')
        process.terminate()
        logger.info('zip process was killed')
        raise
    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archivate),
        web.get('/test', uptime_handler),
    ])
    web.run_app(app)
