# -*- mode: python -*-

block_cipher = None


a = Analysis(['network_scanner.py'],
             pathex=['C:\\Users\\James\\Documents\\Code!\\Projects\\network_scanner'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='network_scanner',
          debug=False,
          strip=None,
          upx=True,
          console=True)
