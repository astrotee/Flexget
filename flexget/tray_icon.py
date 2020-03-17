import logging
import webbrowser
from functools import partial
from pathlib import Path

from loguru import logger
from PIL import Image
from pystray import Menu, MenuItem

from flexget import __version__

logger = logger.bind(name='tray_icon')


class TrayIcon:
    def __init__(self, path_to_image: Path = Path('flexget') / 'resources' / 'flexget.png'):
        # Silence PIL noisy logging
        logging.getLogger('PIL.PngImagePlugin').setLevel(logging.INFO)
        logging.getLogger('PIL.Image').setLevel(logging.INFO)

        self.path_to_image = path_to_image
        self.icon = None
        self._menu = None

        self.menu_items = []
        self.running = False

        self.add_default_menu_items()

    def add_menu_item(
        self,
        text: str = None,
        action: callable = None,
        menu_item: MenuItem = None,
        index: int = None,
        **kwargs,
    ):
        """
        Add a menu item byt passing its text and function, or pass a created MenuItem. Force position by sending index
        """
        if not any(v for v in (menu_item, text)):
            raise ValueError(f"Either 'text' or 'menu_item' are required")

        menu_item = menu_item or MenuItem(text=text, action=action, **kwargs)
        if index is not None:
            self.menu_items.insert(index, menu_item)
        else:
            self.menu_items.append(menu_item)

    def add_menu_separator(self, index: int = None):
        self.add_menu_item(menu_item=Menu.SEPARATOR, index=index)

    def add_default_menu_items(self):
        web_page = partial(webbrowser.open)
        self.add_menu_item(text=f'Flexget {__version__}', enabled=False)
        self.add_menu_separator()
        self.add_menu_item(text='Homepage', action=partial(web_page, 'https://flexget.com/'))
        self.add_menu_item(text='Forum', action=partial(web_page, 'https://discuss.flexget.com/'))

    @property
    def menu(self) -> Menu:
        # This is lazy loaded since we'd like to delay the menu build until the tray is requested to run
        if not self._menu:
            self._menu = Menu(*self.menu_items)
        return self._menu

    def run(self):
        try:
            # This import is here since it can causes crashes on certain conditions,
            # like trying load Icon in linux without X running
            from pystray import Icon

            logger.verbose('Starting tray icon')
            self.icon = Icon('Flexget', Image.open(self.path_to_image), menu=self.menu)
            self.running = True
            self.icon.run()  # This call is blocking and must be done from main thread
        except Exception as e:
            logger.warning('Could not run tray icon: {}', e)
            self.running = False

    def stop(self):
        logger.verbose('Stopping tray icon')
        self.icon.stop()
        self.running = False


try:
    tray_icon = TrayIcon()
except Exception as e:
    logger.warning('Could not load tray icon: {}', e)
    tray_icon = None
