project(
  'Fortuna',
  ['c', 'cpp', 'cython'],
  version: '6.1.1',
  meson_version: '>=1.6.0',
  default_options: [
    'cpp_std=c++20',
    'warning_level=2',
  ],
)

python = import('python').find_installation(pure: false)

python.extension_module(
  '_core',
  'src/Fortuna/_core.pyx',
  include_directories: include_directories('src/Fortuna/vendor'),
  override_options: ['cython_language=cpp'],
  subdir: 'Fortuna',
  install: true,
)

python.install_sources(
  [
    'src/Fortuna/__init__.py',
    'src/Fortuna/_core.pyi',
    'src/Fortuna/_selectors.py',
    'src/Fortuna/py.typed',
  ],
  subdir: 'Fortuna',
)
