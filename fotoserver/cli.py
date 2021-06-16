import argparse
import os

def parse_arguments():
    default_directory = os.path.join(os.getcwd(), 'test_photos')
    parser = argparse.ArgumentParser(description='Сервер скачивания фотоархива')
    parser.add_argument('-d', '--delay', type=int, default=0,
                        help='Задержка перед отправкой Чанка в секундах')
    parser.add_argument('-dir', '--directory', default=default_directory,
                        help='Путь до директории с фото')
    parser.add_argument('--no-logging', action='store_true',
                        help='Отключить Логгирование по дефолту включено')
    args = parser.parse_args()
    return args
