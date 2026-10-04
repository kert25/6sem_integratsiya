# ЛР6 — автотесты Wikipedia Android

## Подготовка окружения

1. Создать и запустить AVD `LR6_Pixel_6` (Pixel 6, API 30+).
2. В Google Play установить **Wikipedia** (`org.wikipedia`).
3. Убедиться, что устройство доступно: `adb devices`.
4. Запустить сервер: `appium`.

## Запуск

Из каталога `mobile_tests`:

```sh
py -m pytest --alluredir=reports/allure
allure generate reports/allure --clean -o reports/allure-html
```

Параметры можно переопределить переменными окружения: `APPIUM_URL`,
`ANDROID_DEVICE_NAME`, `ANDROID_PLATFORM_VERSION`, `ANDROID_UDID` и
`WIKIPEDIA_APK`.

Тесты покрывают поиск статьи и открытие статьи из выдачи. После установки
Wikipedia на выбранной версии Android необходимо подтвердить локаторы
фактическим прогоном.
