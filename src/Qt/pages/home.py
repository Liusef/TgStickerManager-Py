import asyncio
import os
from logging import debug

from PySide6.QtCore import QTimer
from PySide6.QtGui import Qt, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from qasync import asyncSlot

from src import gvars
from src.Qt import gui
from src.Qt.gui import Loading
from src.Qt.ClickWidget import ClickWidget
from src.Qt.GridView import GridView
from src.Tg import tgapi
from src.Tg import stickers
from src.Tg.stickers import TgStickerPack

# TODO Do proper docstrings on this file


class HomePage(QWidget):
    """
    The main Homepage widget. Instantiate this one!!
    """
    def __init__(self, title: str = "Telegram Stickers"):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignHCenter)

        title = gui.basic_label(title, gui.generate_font(32, QFont.Bold))
        title.setContentsMargins(20, 20, 20, 20)

        self.layout().addWidget(gui.nest_widget(title, Qt.AlignTop))
        self.pgv = _PackGridView()
        self.layout().addWidget(nest := self.pgv)
        nest.setStyleSheet("background-color: #24282c")

        buttons = QWidget()
        buttons.setLayout(QHBoxLayout())
        buttons.layout().setAlignment(Qt.AlignRight)
        buttons.layout().addStretch()
        buttons.setContentsMargins(20, 20, 20, 20)

        add = QPushButton()
        add.setText("New")
        add.clicked.connect(self.add_page)
        add.setFont(gui.generate_font(11, QFont.Medium))
        add.setFixedSize(100, 30)
        buttons.layout().addWidget(add)

        re = QPushButton()
        re.setText("Refresh")
        re.clicked.connect(self.refresh)
        re.setFont(gui.generate_font(11, QFont.Medium))
        re.setFixedSize(100, 30)
        buttons.layout().addWidget(re)

        self.layout().addWidget(buttons)

    def add_page(self):
        print("I haven't implemented this oops")
        pass

    @asyncSlot()
    async def refresh(self):
        await stickers.update_owned_packs()
        await self.pgv.show_info()


from src.Qt.pages.base_sticker import BaseStickerPage


class _PackWidget(ClickWidget):
    def __init__(self, pack: TgStickerPack):
        super().__init__()
        self.pack = pack
        thumb = gui.get_pixmap_from_file(self.pack.get_thumb_path())
        tlabel = QLabel()
        tlabel.setScaledContents(True)
        tlabel.setFixedSize(80, 80)
        tlabel.setContentsMargins(0, 0, 0, 0)
        tlabel.setPixmap(thumb)
        tnest = gui.nest_widget(tlabel)

        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignCenter)
        self.layout().addWidget(tnest)

        text = gui.basic_label(pack.name, alignment=Qt.AlignCenter)
        text.setContentsMargins(2, 2, 2, 2)

        self.layout().addWidget(text)
        self.layout().setContentsMargins(2, 2, 2, 2)
        self.layout().setSpacing(2)

        self.setStyleSheet('background-color: none')

        self.clicked.connect(self.pack_page)

    @asyncSlot()
    async def pack_page(self):
        self.parentWidget().parentWidget().parentWidget().parentWidget().layout().addWidget(Loading())
        await asyncio.sleep(0.01)
        self.parentWidget().parentWidget().parentWidget().parentWidget().parentWidget().parentWidget().\
            setCentralWidget(BaseStickerPage(self.pack))


class _PackGridView(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignCenter)
        self.gv = GridView(5, 140, 140, False)
        self.loading = Loading()
        self.gv.setStyleSheet('border: none')
        self.show_info()

    def clear_layout(self):
        self.loading.deleteLater()
        self.loading = Loading()
        for i in range(self.layout().count()):
            self.layout().removeWidget(self.layout().itemAt(0).widget())

    @asyncSlot()
    async def show_info(self):
        self.layout().addWidget(self.loading)
        sns: list[str] = await stickers.get_owned_packs()
        debug(f"Got owned packs: {sns}")
        if len(sns) == 0:
            debug("owned packs len == 0, displaying 0 packs screen")
            self.clear_layout()
            self.layout().addWidget(gui.basic_label("You don't have any Sticker Packs\n"
                                                    "Press Refresh to sync your packs from Telegram or Add to create a "
                                                    "new pack!",
                                                    font=gui.generate_font(12)))
        else:
            debug("getting packs and adding to gridview")
            packs: list[TgStickerPack] = [await stickers.get_pack(s) for s in sns]
            self.gv.set_contents([_PackWidget(tgs) for tgs in packs])
            debug("showing gridview...")
            self.clear_layout()
            self.layout().addWidget(self.gv)
