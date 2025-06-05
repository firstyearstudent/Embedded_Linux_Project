import os
import importlib.util

class PluginLoader:
    def __init__(self, plugins_dir):
        self.plugins_dir = plugins_dir
        self.plugins = []

    def load_plugins(self):
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith('_plugin.py'):
                plugin_path = os.path.join(self.plugins_dir, filename)
                spec = importlib.util.spec_from_file_location(filename[:-3], plugin_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.plugins.append(module)

    def handle_device(self, device, action):
        results = []
        for plugin in self.plugins:
            if hasattr(plugin, 'can_handle') and plugin.can_handle(device):
                if hasattr(plugin, 'handle'):
                    results.append(plugin.handle(device, action))
                else:
                    results.append(f"Handled by {plugin.__name__}")
        return results if results else None
