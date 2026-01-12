## Сборка приложения

```shell
python -m scripts.builder --version "<tag>" --path main.py --icon-path main_icon.ico --onefile --additional-files release_manifest.json, tray_image.png, settings.yml, locations.yml, logger.yml
```

## Публикация релиза
```shell
python -m scripts.release --tag "<tag>" --manifest <manifest/path> --assets <assets/path>
```