#!/usr/bin/env python3
"""Create a local Mac app launcher; Homebrew dependencies stay on this machine."""
from pathlib import Path
import plistlib
import shutil
root = Path(__file__).resolve().parents[1]
game = root / 'game_chinese'
app = game / '洞窟物语中文版.app'
contents = app / 'Contents'
(contents / 'MacOS').mkdir(parents=True, exist_ok=True)
(contents / 'Resources').mkdir(exist_ok=True)
shutil.copy2(game / 'CSE2', contents / 'MacOS/CSE2')
# SDL_GetBasePath returns Contents/Resources for a Mac app. Point it at the
# prepared game data without duplicating it; this launcher stays with game_chinese.
link = contents / 'Resources/data'
if not link.exists():
    link.symlink_to('../../../data', target_is_directory=True)
with (contents / 'Info.plist').open('wb') as f:
    plistlib.dump(dict(CFBundleExecutable='CSE2', CFBundleIdentifier='local.cse2.chinese',
        CFBundleName='洞窟物语中文版', CFBundleDisplayName='洞窟物语中文版',
        CFBundlePackageType='APPL', CFBundleVersion='1',
        NSHighResolutionCapable=False), f)
command = root / '启动中文版.command'
command.write_text('#!/bin/bash\nset -e\ncd "$(dirname "$0")/game_chinese"\nexec ./CSE2\n')
command.chmod(0o755)
print('Local Mac launcher:', app)
