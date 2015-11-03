import os, abc, shutil, io, functools
from pygments import formatters
from .. import util, js
from ..easyxml.namespaces import xhtml


class AssetFile:
	def __init__(self, relative_path : str, stream_factory : callable):
		self._relative_path = relative_path
		self._stream_factory = stream_factory
	
	def write_file(self, dest_dir):
		dest_path = os.path.join(dest_dir, self._relative_path)
		dir = os.path.dirname(dest_path)
		
		if not os.path.exists(dir):
			os.makedirs(dir)
		
		with self._stream_factory() as src_file, open(dest_path, 'wb') as dest_file:
			shutil.copyfileobj(src_file, dest_file)


def create_bytes_file(relative_path, resource_content_factory):
	def content_factory():
		return io.BytesIO(resource_content_factory())
	
	return AssetFile(relative_path, content_factory)


class Asset:
	def __init__(self, files : list, header_fragment : list):
		self.files = files
		self.header_fragment = header_fragment


class AssetFactory(metaclass = abc.ABCMeta):
	_dest_asset_dir = 'assets'
	
	@abc.abstractmethod
	def prepare(self) -> Asset: pass


def _create_css_header_elem(path):
	return xhtml.link(rel = 'stylesheet', type = 'text/css', href = path)


def _create_js_header_elem(path):
	return xhtml.script(type = 'text/javascript', src = path)


class ResourceAssetFactory(AssetFactory):
	_resources_dir = 'resources'
	
	_header_elem_factories = dict(
		css = _create_css_header_elem,
		js = _create_js_header_elem)
	
	def __init__(self, name : str):
		self._name = name
	
	def prepare(self) -> Asset:
		asset_resources_dir = os.path.join(self._resources_dir, self._name)
		files = []
		header_fragment = []
		
		for i in util.list_resources(asset_resources_dir):
			ext = os.path.splitext(i)[1][1:]
			dest_path = os.path.join(self._dest_asset_dir, os.path.relpath(i, asset_resources_dir))
			
			header_elem_factory = self._header_elem_factories.get(ext)
			content_factory = functools.partial(util.get_resource, i)
			
			if header_elem_factory:
				header_fragment.append(header_elem_factory(dest_path))
			
			files.append(create_bytes_file(dest_path, content_factory))
		
		return Asset(files, header_fragment)


class PygmentsAssetFactory(AssetFactory):
	_css_file_name = 'pygments.css'
	
	def prepare(self) -> Asset:
		css_path = os.path.join(self._dest_asset_dir, self._css_file_name)
		
		return Asset(
			[create_bytes_file(css_path, self._get_pygments_css)],
			[_create_css_header_elem(css_path)])
	
	@classmethod
	def _get_pygments_css(cls):
		return formatters.HtmlFormatter().get_style_defs('.highlight').encode()


slidy = ResourceAssetFactory('slidy')
katex = ResourceAssetFactory('katex')
pygments = PygmentsAssetFactory()
