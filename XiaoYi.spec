# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['model/wakeup_xiaoyitx.table'],
    binaries=[],
    datas=[
         ('dll/Microsoft.CognitiveServices.Speech.core.dll', '.'),
         ('dll/Microsoft.CognitiveServices.Speech.extension.audio.sys.dll', '.'),
         ('dll/Microsoft.CognitiveServices.Speech.extension.codec.dll', '.'),
         ('dll/Microsoft.CognitiveServices.Speech.extension.kws.dll', '.'),
         ('dll/Microsoft.CognitiveServices.Speech.extension.lu.dll', '.'),
         ('model/wakeup_xiaoyitx.table', './model'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='XiaoYi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='XiaoYi',
)
