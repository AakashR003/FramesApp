# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('app.py', '.'), ('pages', 'pages'), ('StructuralElements.py', '.'), ('Loads.py', '.'), ('FirstOrderResponse.py', '.'), ('SecondOrderResponse.py', '.'), ('FiniteElementDivisor.py', '.'), ('config.py', '.'), ('data', 'data'), ('.streamlit', '.streamlit')]
binaries = []
hiddenimports = ['streamlit', 'pydeck', 'altair', 'plotly', 'numpy', 'pandas', 'matplotlib', 'scipy']
tmp_ret = collect_all('streamlit')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['run_app_simple.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Structural Analysis App',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Structural Analysis App',
)
