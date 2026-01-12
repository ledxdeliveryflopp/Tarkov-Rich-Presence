import argparse
import json
import logging
import os
import shutil

import PyInstaller.__main__
import yaml
from py7zr import py7zr


def build_app(build_info: list[str]) -> None:
    PyInstaller.__main__.run(build_info)


def check_onefile(one_file_param: bool) -> str | None:
    if one_file_param is True:
        return '--onefile'
    else:
        return None


def copy_additional_files(files: list[str]) -> None:
    print('---КОПИРОВАНИЕ-ДОПОЛНИТЕЛЬНЫХ-ФАЙЛОВ---')
    for file_path in files:
        shutil.copy(file_path, 'dist')


def copy_browser_dir() -> None:
    print('---КОПИРОВАНИЕ-БРАУЗЕРА---')
    shutil.copytree('chrome-win64', 'dist/chrome-win64', dirs_exist_ok=True)


def get_release_files() -> list[str]:
    all_items = os.listdir('dist')
    return all_items


def set_default_app_settings() -> None:
    print('---ВЫСТАВЛЕНИЕ-ДЕФОЛТНЫХ-НАСТРОЕК---')
    with open('dist/settings.yml', 'r') as file:
        data = yaml.safe_load(file)
    data['settings']['core']['debug'] = False
    data['settings']['core']['log_folder_path'] = '../logs'
    with open('dist/settings.yml', 'w') as file:
        yaml.safe_dump(data, file)


def set_release_version(release_version: str, installer_version: str) -> None:
    print('---ЗАПИСЬ-ИНФОРМАЦИИ-О-РЕЛИЗЕ---')
    with open('dist/release_manifest.json', 'r') as file:
        data = json.load(file)
    data['tag'] = release_version
    data['installer_required'] = installer_version
    with open('dist/release_manifest.json', 'w') as new_file:
        json.dump(data, new_file, indent=4)


def zip_release():
    print('---АРХИВИРОВАНИЕ-РЕЛИЗА---')
    files = get_release_files()
    with py7zr.SevenZipFile('dist/dist.7z', 'w') as archive:
        for file in files:
            file_path = f'dist/{file}'
            print(file_path)
            if os.path.isdir(file_path):
                archive.writeall(path=file_path, arcname=file)
            else:
                archive.write(file_path, arcname=file)


def build_app_spec(build_params: argparse.Namespace) -> list[str]:
    windowed_mode = '--windowed'
    main_file_path = build_params.path
    main_file_ico = build_params.icon_path
    onefile = build_params.onefile
    onefile_param = check_onefile(one_file_param=onefile)
    app_base_spec = [main_file_path, '--name=EFTDRP', '--icon', main_file_ico]
    if onefile_param:
        app_base_spec.append(onefile_param)
    app_base_spec.append(windowed_mode)
    return app_base_spec


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument('--version', type=str, help='Версия сборки', required=True)
    parser.add_argument('--installer-version', type=str, help='Версия установщика', required=True)
    parser.add_argument('--path', type=str, help='Целевой файл сборки', required=True)
    parser.add_argument('--icon-path', type=str, help='Файл иконки', required=True)
    parser.add_argument('--onefile', action='store_true', help='Упаковка в один файл')
    parser.add_argument('--no-onefile', action='store_false', dest='onefile', help='Упаковка в несколько файлов')
    parser.set_defaults(onefile=False)
    parser.add_argument('--additional-files', nargs='*', help='Файлы для добавления в директорию', required=True)

    args = parser.parse_args()
    return args


def clear_dist_dir() -> None:
    print('---ОЧИСТКА-ПАПКИ-СБОРКИ---')
    path_exist = os.path.exists('dist')
    if path_exist is True:
        shutil.rmtree('dist')
        print('---ПАПКИ-СБОРКИ-ОЧИЩЕНА---')


if __name__ == '__main__':
    logging.disable(logging.ERROR)
    print('---НАЧАЛО-СБОРКИ---')
    params = parse_args()
    clear_dist_dir()
    app_spec = build_app_spec(build_params=params)
    build_app(build_info=app_spec)
    copy_additional_files(files=params.additional_files)
    set_default_app_settings()
    set_release_version(release_version=params.version, installer_version=params.installer_version)
    copy_browser_dir()
    zip_release()
    print('---СБОРКА-ЗАВЕРШЕНА---')
