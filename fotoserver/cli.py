import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description='Сервер скачивания фотоархива')
    parser.add_argument('-d', '--delay', type=int, default=0,
                        help='Задержка перед отправкой Чанка в секундах')
    parser.add_argument('-dir', '--directory', default=None,
                        help='Путь до директории с фото')
    parser.add_argument('--no-logging', action='store_true',
                        help='Отключить Логгирование по дефолту включено')
    args = parser.parse_args()
    return args
