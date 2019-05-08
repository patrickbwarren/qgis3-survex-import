PLUGIN = survex_import
QGIS3_PROFILE = ~/.local/share/QGIS/QGIS3/profiles/default
QGIS3_PYTHON_PLUGINS = $(QGIS3_PROFILE)/python/plugins

SOURCE = ./src
DEPLOY = ./$(PLUGIN)

default: build install

build:
	cd src; yes | pb_tool deploy

install:
	cp -R $(DEPLOY) $(QGIS3_PYTHON_PLUGINS)
