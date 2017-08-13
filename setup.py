# -*- coding: utf-8 -*-

import sys
from cx_Freeze import setup, Executable

# Add the underlying folder hiearchy
options = {
	'build_exe': {
		'include_files': [('app/', 'app/')]
	}
}

executables = [
	Executable('RWITData.py'),
]

setup(name='RWITData',
	  version='0',
	  description='RWITData',
	  options=options,
	  executables=executables
	  )