import os, abc, shutil, io
from pygments import formatters
from .. import util
from ..easyxml.namespaces import xhtml


class AssetFile(metaclass = abc.ABCMeta):
	def __init__(self, *, relative_path : str):
		self._relative_path = relative_path
	
	@abc.abstractmethod
	def _write_file(self, dest_path): pass
	
	def _link_file(self, dest_path):
		self._write_file(dest_path)
	
	def write(self, dest_dir, link_file : bool):
		dest_path = os.path.join(dest_dir, self._relative_path)
		dir = os.path.dirname(dest_path)
		
		if not os.path.exists(dir):
			os.makedirs(dir)
		
		if os.path.exists(dest_path):
			os.unlink(dest_path)
		
		if link_file:
			self._link_file(dest_path)
		else:
			self._write_file(dest_path)


class GeneratedAssetFile(AssetFile):
	def __init__(self, *, stream_factory : callable, **kwargs):
		super().__init__(**kwargs)
		
		self._stream_factory = stream_factory
	
	def _write_file(self, dest_path):
		with self._stream_factory() as src_file, open(dest_path, 'wb') as dest_file:
			shutil.copyfileobj(src_file, dest_file)


class CopiedAssetFile(AssetFile):
	def __init__(self, *, path : str, **kwargs):
		super().__init__(**kwargs)
		
		self._path = path
	
	def _link_file(self, dest_path):
		os.symlink(self._path, dest_path)
	
	def _write_file(self, dest_path):
		shutil.copyfile(self._path, dest_path)


class ResourceAssetFile(AssetFile):
	def __init__(self, *, name : str, **kwargs):
		super().__init__(**kwargs)
		
		self._name = name
	
	def _link_file(self, dest_path):
		os.symlink(util.get_resource_path(self._name), dest_path)
	
	def _write_file(self, dest_path):
		with util.get_resource_stream(self._name) as src_file, open(dest_path, 'wb') as dest_file:
			shutil.copyfileobj(src_file, dest_file)


def create_bytes_file(relative_path, resource_content_factory):
	def stream_factory():
		return io.BytesIO(resource_content_factory())
	
	return GeneratedAssetFile(relative_path = relative_path, stream_factory = stream_factory)


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
			
			if header_elem_factory:
				header_fragment.append(header_elem_factory(dest_path))
			
			files.append(ResourceAssetFile(relative_path = dest_path, name = i))
		
		return Asset(files, header_fragment)


class PygmentsAssetFactory(AssetFactory):
	_css_file_name = 'pygments.css'
	
	def prepare(self) -> Asset:
		css_path = os.path.join(self._dest_asset_dir, self._css_file_name)
		
		return Asset(
			[GeneratedAssetFile(
				relative_path = css_path,
				stream_factory = self._get_pygments_css_stream)],
			[_create_css_header_elem(css_path)])
	
	@classmethod
	def _get_pygments_css_stream(cls):
		content = formatters.HtmlFormatter(style = 'colorful').get_style_defs('.highlight')
		
		return io.BytesIO(content.encode())


upshot = ResourceAssetFactory('upshot')
katex = ResourceAssetFactory('katex')
pygments = PygmentsAssetFactory()
