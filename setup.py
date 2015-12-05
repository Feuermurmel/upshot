import setuptools


setuptools.setup(
	name = 'Upshot',
	version = '0.1',
	packages = setuptools.find_packages(),
	package_data = { '': ['*.*'] },
	install_requires = ['setuptools', 'markdown', 'pygments', 'py-gfm', 'python-markdown-math', 'pyexecjs', 'pystache', 'nodeenv'],
	entry_points = dict(
		console_scripts = [
			'upshot = upshot:script_main']))
