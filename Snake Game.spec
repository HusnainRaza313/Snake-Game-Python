# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['snake_game.py'],
    pathex=[],
    binaries=[],
    datas=[('background_music.wav', '.'), ('best_badge.png', '.'), ('glass_card.png', '.'), ('pause_btn_hover.png', '.'), ('pause_btn_normal.png', '.'), ('play_again_btn_hover.png', '.'), ('play_again_btn_normal.png', '.'), ('resume_btn_hover.png', '.'), ('resume_btn_normal.png', '.'), ('score_badge.png', '.'), ('snake_background.png', '.'), ('snake_body.png', '.'), ('snake_food.png', '.'), ('snake_head.png', '.'), ('start_background.png', '.'), ('start_btn_hover.png', '.'), ('start_btn_normal.png', '.')],
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
    name='Snake Game',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['valid_icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Snake Game',
)
