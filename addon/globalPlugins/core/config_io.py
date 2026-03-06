# -*- coding: utf-8 -*-

import copy
import json
import os

from .constants import TEXT_SNIPPET_ACTION_VALUES, TYPE_SECTIONS, VERBOSITY_VALUES


def _defaultConfig():
	return {
		"version": 1,
		"settings": {"verbosity": VERBOSITY_VALUES[0]},
		"items": [],
	}


def _normalizeItem(rawItem):
	if not isinstance(rawItem, dict):
		return None
	name = (rawItem.get("name", "") or "").strip()
	itemType = (rawItem.get("type", "") or "").strip()
	path = rawItem.get("path", "")
	gesture = (rawItem.get("gesture", "") or "").strip().lower()
	arguments = (rawItem.get("arguments", "") or "").strip()
	textAction = (rawItem.get("textAction", TEXT_SNIPPET_ACTION_VALUES[0]) or "").strip().lower()
	commandLabel = (rawItem.get("commandLabel", "") or "").strip()
	appName = (rawItem.get("appName", "") or "").strip().lower()
	if itemType not in TYPE_SECTIONS:
		return None
	if not name or not gesture:
		return None
	if not isinstance(path, str):
		path = ""
	if textAction not in TEXT_SNIPPET_ACTION_VALUES:
		textAction = TEXT_SNIPPET_ACTION_VALUES[0]
	return {
		"name": name,
		"type": itemType,
		"path": path,
		"gesture": gesture,
		"arguments": arguments,
		"textAction": textAction,
		"commandLabel": commandLabel,
		"appName": appName,
	}


def _normalizeConfig(rawConfig):
	if not isinstance(rawConfig, dict):
		raise ValueError("Invalid config format")
	settings = rawConfig.get("settings", {})
	if not isinstance(settings, dict):
		settings = {}
	verbosity = (settings.get("verbosity", VERBOSITY_VALUES[0]) or "").strip().lower()
	if verbosity not in VERBOSITY_VALUES:
		verbosity = VERBOSITY_VALUES[0]
	rawItems = rawConfig.get("items", [])
	if not isinstance(rawItems, list):
		rawItems = []
	items = []
	for rawItem in rawItems:
		item = _normalizeItem(rawItem)
		if item is not None:
			items.append(item)
	return {
		"version": 1,
		"settings": {"verbosity": verbosity},
		"items": items,
	}


def ensureConfigFile(configPath):
	configDir = os.path.dirname(configPath)
	os.makedirs(configDir, exist_ok=True)
	if not os.path.exists(configPath):
		saveConfig(configPath, _defaultConfig())


def saveConfig(configPath, config):
	configDir = os.path.dirname(configPath)
	os.makedirs(configDir, exist_ok=True)
	normalized = _normalizeConfig(config)
	with open(configPath, "w", encoding="utf-8") as handle:
		json.dump(normalized, handle, ensure_ascii=False, indent="\t")


def loadConfigSafe(configPath):
	ensureConfigFile(configPath)
	try:
		with open(configPath, "r", encoding="utf-8") as handle:
			rawConfig = json.load(handle)
		return _normalizeConfig(rawConfig)
	except Exception:
		defaultConfig = _defaultConfig()
		saveConfig(configPath, defaultConfig)
		return copy.deepcopy(defaultConfig)


def loadConfigFromPathStrict(configPath):
	with open(configPath, "r", encoding="utf-8") as handle:
		rawConfig = json.load(handle)
	return _normalizeConfig(rawConfig)
