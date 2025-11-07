"""
Optional dependency handler for KOMIHUB Bot
Provides fallback mechanisms for missing optional dependencies
"""
import importlib
import logger
from typing import Optional, Any

class OptionalDependency:
    """Handle optional dependencies with graceful fallbacks"""
    
    def __init__(self, package_name: str, fallback_name: str = None):
        self.package_name = package_name
        self.fallback_name = fallback_name
        self._module = None
        self._loaded = False
    
    def load(self) -> Optional[Any]:
        """Try to load the dependency, return None if not available"""
        if self._loaded:
            return self._module
        
        try:
            self._module = importlib.import_module(self.package_name)
            self._loaded = True
            logger.debug(f"Successfully loaded optional dependency: {self.package_name}")
            return self._module
        except ImportError as e:
            if self.fallback_name:
                try:
                    self._module = importlib.import_module(self.fallback_name)
                    self._loaded = True
                    logger.debug(f"Loaded fallback dependency: {self.fallback_name}")
                    return self._module
                except ImportError:
                    logger.warning(f"Optional dependency {self.package_name} and fallback {self.fallback_name} not available")
            else:
                logger.warning(f"Optional dependency {self.package_name} not available: {e}")
            return None
    
    def __getattr__(self, name: str) -> Any:
        """Get attributes from the loaded module"""
        module = self.load()
        if module is not None:
            return getattr(module, name)
        raise AttributeError(f"Module {self.package_name} not available")

# Define optional dependencies
toml = OptionalDependency("toml")
pyqrcode = OptionalDependency("pyqrcode", "pyqrcode")
qrcode = OptionalDependency("qrcode", "qrcode")
pypng = OptionalDependency("pypng")

def check_optional_deps():
    """Check which optional dependencies are available"""
    available_deps = {
        "toml": toml.load() is not None,
        "pyqrcode": pyqrcode.load() is not None,
        "qrcode": qrcode.load() is not None,
        "pypng": pypng.load() is not None
    }
    
    logger.info("Optional dependencies check:")
    for dep, available in available_deps.items():
        status = "✅" if available else "❌"
        logger.info(f"  {status} {dep}")
    
    return available_deps

def get_qr_code_generators():
    """Get available QR code generation functions"""
    generators = []
    
    # Try pyqrcode first
    pyqr_module = pyqrcode.load()
    if pyqr_module:
        generators.append(("pyqrcode", pyqr_module.create))
    
    # Try qrcode library as fallback
    qr_module = qrcode.load()
    if qr_module:
        generators.append(("qrcode", qr_module.make))
    
    return generators

def safe_import_toml():
    """Safely import toml with fallback"""
    toml_module = toml.load()
    if toml_module:
        return toml_module
    else:
        logger.warning("toml library not available - config validation will be limited")
        return None