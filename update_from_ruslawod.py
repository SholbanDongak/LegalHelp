#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path.home() / "LegalHelp"
REPO_DIR = PROJECT_DIR / "RusLawOD_repo"
XML_TARGET_DIR = PROJECT_DIR / "RusLawOD_XML"

def update_repo():
    print("Обновление репозитория RusLawOD...")
    os.chdir(REPO_DIR)
    result = subprocess.run(["git", "pull"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Ошибка git pull:", result.stderr)
        sys.exit(1)
    print(result.stdout)

def copy_new_xml():
    print("Поиск новых XML-файлов...")
    repo_files = set(REPO_DIR.glob("*.xml"))
    target_files = set(XML_TARGET_DIR.glob("*.xml"))
    new_files = repo_files - target_files

    if not new_files:
        print("Новых файлов нет.")
        return 0

    print(f"Найдено {len(new_files)} новых файлов.")
    for f in new_files:
        shutil.copy2(f, XML_TARGET_DIR / f.name)
        print(f"Скопирован: {f.name}")
    return len(new_files)

def run_load_script():
    print("Запуск load_to_chromadb.py...")
    os.chdir(PROJECT_DIR)
    subprocess.run(["python", "load_to_chromadb.py"], check=True)

def main():
    if not REPO_DIR.exists():
        print("Папка с репозиторием не найдена. Сначала клонируйте репозиторий.")
        sys.exit(1)
    if not XML_TARGET_DIR.exists():
        print("Папка RusLawOD_XML не найдена.")
        sys.exit(1)

    update_repo()
    count = copy_new_xml()
    if count > 0:
        run_load_script()
    else:
        print("Обновление не требуется.")

if __name__ == "__main__":
    main()