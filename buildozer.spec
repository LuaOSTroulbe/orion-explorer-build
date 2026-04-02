[app]
title = Orion Explorer
package.name = orionexploreroffic
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.1
requirements = python3, kivy==2.3.0, kivymd==1.2.0, pillow, android
orientation = portrait
fullscreen = 0
icon.filename = icon.png

# Android permissions
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# Android API (33 для RuStore)
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# Buildozer settings
[buildozer]
log_level = 2
warn_on_root = 1
