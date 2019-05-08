PLUGIN = survex_import
QGIS3_PROFILE = ~/.local/share/QGIS/QGIS3/profiles/default
QGIS3_PYTHON_PLUGINS = $(QGIS3_PROFILE)/python/plugins
QGIS3_SURVEX_PLUGIN = $(QGIS3_PYTHON_PLUGINS)/$(PLUGIN)

SOURCE = ./src
DEPLOY = ./$(PLUGIN)

default: build install

build:
	cd src; yes | pb_tool deploy

install:
	mkdir -p $(QGIS3_SURVEX_PLUGIN)
	cp -v $(DEPLOY)/icon.png $(QGIS3_SURVEX_PLUGIN)
	cp -v $(DEPLOY)/metadata.txt $(QGIS3_SURVEX_PLUGIN)
	cp -v $(DEPLOY)/*.py $(QGIS3_SURVEX_PLUGIN)
	cp -v $(DEPLOY)/*.ui $(QGIS3_SURVEX_PLUGIN)
