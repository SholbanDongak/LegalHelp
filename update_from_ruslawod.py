#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path.home() / "LegalHelp"
REPO_DIR = PROJECT_DIR / "RusLawOD_repo"
XML_TARGET_DIR = PROJECT_DIR / "RusLawOD_XML"
LOG_FILE = PROJECT_DIR / "logs" / "update.log"

# Настройка логирования
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def update_repo():
    logger.info("Обновление репозитория RusLawOD...")
    os.chdir(REPO_DIR)
    result = subprocess.run(["git", "pull"], capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("Ошибка git pull: " + result.stderr)
        sys.exit(1)
    logger.info(result.stdout.strip())


def copy_new_xml():
    logger.info("Поиск новых XML-файлов...")
    repo_files = set(REPO_DIR.glob("*.xml"))
    target_files = set(XML_TARGET_DIR.glob("*.xml"))
    new_files = repo_files - target_files

    if not new_files:
        logger.info("Новых файлов нет.")
        return 0

    logger.info(f"Найдено {len(new_files)} новых файлов.")
    for f in new_files:
        shutil.copy2(f, XML_TARGET_DIR / f.name)
        logger.info(f"Скопирован: {f.name}")
    return len(new_files)


def run_load_script():
    logger.info("Запуск load_to_chromadb.py...")
    os.chdir(PROJECT_DIR)
    subprocess.run(["python", "load_to_chromadb.py"], check=True)


def main():
    if not REPO_DIR.exists():
        logger.error("Папка с репозиторием не найдена.")
        sys.exit(1)
    if not XML_TARGET_DIR.exists():
        logger.error("Папка RusLawOD_XML не найдена.")
        sys.exit(1)

    update_repo()
    count = copy_new_xml()
    if count > 0:
        run_load_script()
    else:
        logger.info("Обновление не требуется.")


if __name__ == "__main__":
    main()
