from omegaconf import OmegaConf, DictConfig
from ..path import Path, PackageName, get_package_path_dict


def get_kw_safe(key, **kw):
    if key in kw:
        return kw[key]
    else:
        return None


def dict_to_param(dictionary: dict):
    return OmegaConf.create(dictionary)


def create_class_path_dict(package: str = PackageName, class_name: str = 'BaseParam'):
    pkg_path = get_package_path_dict(package)
    return {'path': {
        'param': str(pkg_path['path']['param'] / f'{class_name}.param'),
        'cache': str(pkg_path['path']['cache'] / f'{class_name}.cache'),
    }}


class BaseParams:
    name: str
    params: DictConfig = OmegaConf.create()

    def __init__(self, package: str = PackageName, **params):
        self.name = type(self).__name__

        # Default Path Params
        self.update_params(create_class_path_dict(package, self.name), {'init_save': False})

        # Loaded Params
        self.load_params(raise_exception=False)

        # Update Params
        self.update_params(OmegaConf.create(params))

        # Store Params
        self.save_params()

    def param_file_path(self):
        return Path(self.params.path.param)

    def save_params(self):
        if self.params.init_save:
            OmegaConf.save(self.params, self.params.path.param)

    def load_params(self, raise_exception=True):
        if raise_exception and not self.param_file_path().exists():
            raise BaseParamsCannotLoadConfFileNotExist()

        if self.param_file_path().exists():
            self.params = OmegaConf.merge(self.params, OmegaConf.load(self.param_file_path()))

    def update_params(self, *args):
        if len(args) > 0:
            for arg in args:
                if isinstance(arg, DictConfig):
                    self.params = OmegaConf.merge(self.params, *args)
                    break
                elif isinstance(arg, dict):
                    self.params = OmegaConf.merge(self.params, OmegaConf.create(arg))


class BaseParamsCannotLoadConfFileNotExist(Exception):
    pass
