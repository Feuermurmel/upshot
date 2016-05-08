import setuptools


setuptools.setup(
	name = 'Upshot',
	version = '0.1',
	packages = ['upshot'],
	package_data = { 'upshot': ['*.*'] },
	install_requires = ['setuptools', 'markdown', 'pygments', 'py-gfm', 'python-markdown-math', 'pyexecjs', 'pystache'],
	entry_points = dict(
		console_scripts = [
			'upshot = upshot:script_main']))
