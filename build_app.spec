# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
# Collect data files from ALL packages that need them
trafilatura_datas = collect_data_files('trafilatura')
newspaper_datas = collect_data_files('newspaper')
justext_datas = collect_data_files('justext')
certifi_datas = collect_data_files('certifi')
courlan_datas = collect_data_files('courlan')
htmldate_datas = collect_data_files('htmldate')
dateutil_datas = collect_data_files('dateutil')
charset_norm_datas = collect_data_files('charset_normalizer')
flet_datas = collect_data_files('flet')
block_cipher = None
ROOT = os.path.abspath('.')
# Collect ALL submodules for packages with C extensions
extra_imports = []
for pkg in ['PIL', 'aiohttp', 'lxml', 'charset_normalizer', 'newspaper']:
    extra_imports += collect_submodules(pkg)
a = Analysis(
    ['app/ui/main.py'],
    pathex=[ROOT],
    binaries=[],
    datas=[
        ('data/schema.sql', 'data'),
        ('app/config/scraper_config.json', 'app/config'),
        ('app/config/paywall_signals.json', 'app/config'),
        ('app/config/llm_scoring_config.json', 'app/config'),
        ('app/config/llm_translation_config.json', 'app/config'),
    ] + trafilatura_datas + newspaper_datas + justext_datas
      + certifi_datas + courlan_datas + htmldate_datas
      + dateutil_datas + charset_norm_datas + flet_datas,
    hiddenimports=[
        # Flet
        'flet', 'flet_core', 'flet_runtime',
        # Third-party
        'feedparser', 'trafilatura', 'bs4', 'requests', 'certifi',
        'multidict', 'yarl', 'async_timeout', 'aiosignal', 'frozenlist', 'brotli',
        'courlan', 'htmldate', 'justext', 'dateutil', 'lxml_html_clean',
        # App - UI
        'app', 'app.ui', 'app.ui.main', 'app.ui.theme',
        'app.ui.components', 'app.ui.components.sidebar',
        'app.ui.components.sources_dialog',
        'app.ui.pages', 'app.ui.pages.dashboard', 'app.ui.pages.detail',
        'app.ui.pages.config', 'app.ui.pages.style', 'app.ui.pages.about',
        'app.ui.pages.profiles',
        # App - Services
        'app.services', 'app.services.backend_api',
        'app.services.database_manager', 'app.services.scraper_service',
        'app.services.ai_engine', 'app.services.ollama_engine',
        'app.services.prompt_builder',
        # App - Utils
        'app.utils', 'app.utils.paths', 'app.utils.logger',
        'app.utils.exceptions', 'app.utils.system_check',
        # App - Config
        'app.config', 'app.config.settings',
    ] + extra_imports,
    hookspath=[],
    excludes=[
        # AI/ML frameworks (NOT USED - we use Ollama externally)
        'torch', 'tensorflow', 'keras', 'transformers', 'huggingface',
        'scipy', 'sklearn', 'scikit_learn',
        'numpy', 'pandas', 'matplotlib',
        'cv2', 'opencv', 'opencv_python',
        # Dev tools (NOT NEEDED in prod)
        'pytest', 'jupyter', 'ipython', 'mypy', 'jedi', 'parso',
        'IPython', 'notebook', 'qtconsole', 'jupyter_client',
        'jupyter_core', 'nbformat', 'nbconvert', 'traitlets',
        # NLP (NOT USED)
        'gensim', 'spacy', 'textblob',
        # Browser automation (NOT USED)
        'playwright', 'tkinter',
    ],
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name='AIEAT',
    debug=False,
    strip=False,
    upx=True,
    console=False,
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=True, name='AIEAT',
)
