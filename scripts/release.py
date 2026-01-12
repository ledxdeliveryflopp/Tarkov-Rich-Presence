import argparse
import json
import os
import sys
from http import HTTPStatus
from pprint import pprint

import httpx
from dotenv import load_dotenv

load_dotenv()


class Const:

    owner = 'ledxdeliveryflopp'
    repo = 'Tarkov-Rich-Presence'
    token = os.getenv('TOKEN')

    api_version = '2022-11-28'
    create_url = f'https://api.github.com/repos/{owner}/{repo}/releases'
    upload_asset_url = f'https://uploads.github.com/repos/{owner}/{repo}/releases/'


def get_release_note() -> str:
    print('---ЧТЕНИЕ-ОПИСАНИЯ-РЕЛИЗА---')
    with open('scripts/release_note.md', 'r', encoding='utf-8') as f:
        data = f.read()
    return data


def check_release_manifest_tag(release_tag: str, manifest_path: str) -> None:
    with open(manifest_path, 'r') as f:
        release_manifest_data = json.load(f)
    release_manifest_tag = release_manifest_data['tag']
    if release_manifest_tag == release_tag:
        pass
    else:
        print('НЕ СОВПАДАЮТ ТЭГИ РЕЛИЗА!')
        print(f'Тэг манифеста -> {release_manifest_tag}')
        print(f'Указанный тэг -> {release_tag}')
        sys.exit()


def create_release(release_version: str) -> str:
    print('---СОЗДАНИЕ-РЕЛИЗА---')
    response = httpx.post(
        url=Const.create_url,
        headers={
            'Authorization': f'Bearer {Const.token}',
            'X-GitHub-Api-Version': Const.api_version,
            'Accept': 'application/vnd.github+json',
        },
        json={
            'tag_name': release_version,
            'target_commitish': 'V1.0.0',
            'body': get_release_note(),
            'draft': False,
            'prerelease': False,
            'generate_release_notes': False,
            'make_latest': 'true',
        }
    )
    response_data = response.json()
    if response.status_code == HTTPStatus.CREATED:
        print('---РЕЛИЗ-СОЗДАН---')
        return response_data['id']
    else:
        print('---ОШИБКА-СОЗДАНИЯ-РЕЛИЗА---')
        pprint(response_data)
        sys.exit()


def get_asset_name(asset_path: str) -> str:
    return asset_path.split('/')[-1]


def upload_assets(release_id: str, asset_list: list[str]) -> None:
    print('---ЗАГРУЗКА-АССЕТОВ---')
    print(f'Список ассетов -> {', '.join(i for i in asset_list)}')
    for asset_path in asset_list:
        with open(asset_path, 'rb') as asset_file:
            file_data = asset_file.read()
            asset_name = get_asset_name(asset_path=asset_path)
            response = httpx.post(
                url=f'{Const.upload_asset_url}{release_id}/assets?',
                params={'name': asset_name},
                headers={
                    'Authorization': f'Bearer {Const.token}',
                    'Accept': 'application/vnd.github+json',
                    'X-GitHub-Api-Version': Const.api_version,
                    'content-type': 'multipart/form-data',
                },
                files={'data': file_data},
                timeout=120,
            )
            if response.status_code == HTTPStatus.CREATED:
                print(f'Ассет {asset_name} -> загружен!')
            else:
                print(f'Ошибка загрузки {asset_name}!')
                pprint(response.json())


def upload_manifest(manifest_path: str) -> None:
    print('---ЗАГРУЗКА-МАНИФЕСТА---')
    with open(manifest_path, 'rb') as manifest_file:
        file_data = manifest_file.read()
        asset_name = get_asset_name(asset_path=manifest_path)
        response = httpx.post(
            url=f'{Const.upload_asset_url}{release_id}/assets?',
            params={'name': asset_name},
            headers={
                'Authorization': f'Bearer {Const.token}',
                'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': Const.api_version,
                'content-type': 'multipart/form-data',
            },
            files={'data': file_data},
            timeout=120,
        )
        if response.status_code == HTTPStatus.CREATED:
            print(f'Манифест {asset_name} -> загружен!')
        else:
            print(f'Ошибка загрузки {asset_name}!')
            pprint(response.json())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument('--tag', type=str, help='Тэг релиза', required=True)
    parser.add_argument('--assets', nargs='*', help='Ассеты релиза', required=True)
    parser.add_argument('--manifest', type=str, help='Манифест релиза', required=True)

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    cli_args = parse_args()
    release_tag = cli_args.tag
    manifest_path = cli_args.manifest
    check_release_manifest_tag(release_tag=release_tag, manifest_path=manifest_path)
    asset_list = cli_args.assets
    release_id = create_release(release_version=release_tag)
    upload_assets(release_id=release_id, asset_list=asset_list)
    upload_manifest(manifest_path=manifest_path)
