# -*- coding: utf-8 -*-

from .config_io import ensureConfigFile, loadConfigSafe, saveConfig
from .constants import TYPE_SECTIONS, VERBOSITY_VALUES


class ConfigManager:
	def __init__(self, configPath):
		self.configPath = configPath
		ensureConfigFile(self.configPath)

	def loadOrCreateConfig(self):
		return loadConfigSafe(self.configPath)

	def saveConfig(self, config):
		saveConfig(self.configPath, config)

	def getConfigPath(self):
		return self.configPath

	def _toPublicItem(self, storedItem):
		return {
			"name": storedItem.get("name", ""),
			"type": storedItem.get("type", ""),
			"path": storedItem.get("path", ""),
			"arguments": storedItem.get("arguments", ""),
			"textAction": storedItem.get("textAction", "type"),
			"commandLabel": storedItem.get("commandLabel", ""),
			"appName": (storedItem.get("appName", "") or "").strip().lower(),
			"gestures": [storedItem.get("gesture", "")] if storedItem.get("gesture", "") else [],
		}

	def getItems(self):
		config = self.loadOrCreateConfig()
		items = []
		for storedItem in config.get("items", []):
			items.append(self._toPublicItem(storedItem))
		return items

	def getAllNames(self):
		return {item.get("name", "") for item in self.getItems()}

	def getGestureToNameMap(self):
		gestureMap = {}
		for item in self.getItems():
			name = item.get("name", "")
			for gesture in item.get("gestures", []):
				normalized = (gesture or "").strip().lower()
				if normalized and normalized not in gestureMap:
					gestureMap[normalized] = name
		return gestureMap

	def findGestureConflict(self, gesture, appName="", excludeName=""):
		normalizedGesture = (gesture or "").strip().lower()
		normalizedAppName = (appName or "").strip().lower()
		if not normalizedGesture:
			return None
		for item in self.getItems():
			if excludeName and item.get("name", "") == excludeName:
				continue
			itemAppName = (item.get("appName", "") or "").strip().lower()
			for itemGesture in item.get("gestures", []):
				if (itemGesture or "").strip().lower() != normalizedGesture:
					continue
				if itemAppName == normalizedAppName:
					return item
		return None

	def addItem(self, name, itemType, path, gesture, arguments="", textAction="type", commandLabel="", appName=""):
		config = self.loadOrCreateConfig()
		items = config.get("items", [])
		items = [item for item in items if item.get("name", "") != name]
		items.append(
			{
				"name": name,
				"type": itemType if itemType in TYPE_SECTIONS else TYPE_SECTIONS[0],
				"path": path,
				"gesture": (gesture or "").strip().lower(),
				"arguments": arguments.strip() if itemType == "Programs" else "",
				"textAction": (textAction or "type").strip().lower(),
				"commandLabel": commandLabel.strip() if itemType == "NvdaCommands" else "",
				"appName": (appName or "").strip().lower(),
			},
		)
		config["items"] = items
		self.saveConfig(config)

	def updateItem(
		self,
		oldName,
		name,
		itemType,
		path,
		gesture,
		arguments="",
		textAction="type",
		commandLabel="",
		appName="",
	):
		config = self.loadOrCreateConfig()
		items = [item for item in config.get("items", []) if item.get("name", "") not in (oldName, name)]
		items.append(
			{
				"name": name,
				"type": itemType if itemType in TYPE_SECTIONS else TYPE_SECTIONS[0],
				"path": path,
				"gesture": (gesture or "").strip().lower(),
				"arguments": arguments.strip() if itemType == "Programs" else "",
				"textAction": (textAction or "type").strip().lower(),
				"commandLabel": commandLabel.strip() if itemType == "NvdaCommands" else "",
				"appName": (appName or "").strip().lower(),
			},
		)
		config["items"] = items
		self.saveConfig(config)

	def deleteItem(self, name):
		config = self.loadOrCreateConfig()
		config["items"] = [item for item in config.get("items", []) if item.get("name", "") != name]
		self.saveConfig(config)

	def getVerbosityLevel(self):
		config = self.loadOrCreateConfig()
		settings = config.get("settings", {})
		value = (settings.get("verbosity", VERBOSITY_VALUES[0]) or "").strip().lower()
		if value not in VERBOSITY_VALUES:
			value = VERBOSITY_VALUES[0]
		return value

	def setVerbosityLevel(self, value):
		config = self.loadOrCreateConfig()
		value = (value or "").strip().lower()
		if value not in VERBOSITY_VALUES:
			value = VERBOSITY_VALUES[0]
		config.setdefault("settings", {})
		config["settings"]["verbosity"] = value
		self.saveConfig(config)
