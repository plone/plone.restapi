"""Update locales."""

from pathlib import Path

import logging
import re
import subprocess


logging.basicConfig()
logger = logging.getLogger("i18n")
logger.setLevel(logging.DEBUG)


PATTERN = r"^[a-z]{2}.*"
cwd = Path.cwd()
target_path = Path(__file__).parent.parent.relative_to(cwd)
locale_path = target_path / "locales"


def get_i18ndude() -> Path:
    possible_locations = [
        cwd,
        cwd / "bin",
        cwd / ".venv" / "bin",
    ]
    for path in possible_locations:
        i18ndude = path / "i18ndude"
        if i18ndude.exists():
            return i18ndude
    else:
        raise RuntimeError("Not able to find i18ndude script")


i18ndude = get_i18ndude()

# ignore node_modules files resulting in errors
excludes = '"*.html *json-schema*.xml"'


def _get_languages_folders():
    folders = [path for path in locale_path.glob("*") if path.is_dir()]
    language_folders = sorted(
        [path for path in folders if not path.name.startswith("_")],
        key=lambda item: item.name,
    )
    return language_folders


def locale_folder_setup(domain: str):
    languages = _get_languages_folders()
    for lang_folder in languages:
        lc_messages_path = lang_folder / "LC_MESSAGES"
        lang = lang_folder.name
        if lc_messages_path.exists():
            continue
        elif re.match(PATTERN, lang):
            lc_messages_path.mkdir()
            cmd = (
                f"msginit --locale={lang} "
                f"--input={locale_path}/{domain}.pot "
                f"--output={locale_path}/{lang}/LC_MESSAGES/{domain}.po"
            )
            subprocess.call(
                cmd,
                shell=True,
            )


def _rebuild(domain: str):
    cmd = (
        f"{i18ndude} rebuild-pot --pot {locale_path}/{domain}.pot "
        f"--exclude {excludes} "
        f"--create {domain} {target_path}"
    )
    subprocess.call(
        cmd,
        shell=True,
    )


def _sync(domain: str):
    for path in locale_path.glob("*/LC_MESSAGES/"):
        # Check if domain file exists
        domain_file = path / f"{domain}.po"
        if not domain_file.exists():
            # Create an empty file
            domain_file.write_text("")
    cmd = (
        f"{i18ndude} sync --pot {locale_path}/{domain}.pot "
        f"{locale_path}/*/LC_MESSAGES/{domain}.po"
    )
    subprocess.call(
        cmd,
        shell=True,
    )


def update_locale():
    domains = [path.name[:-4] for path in locale_path.glob("*.pot")]
    if i18ndude.exists():
        for domain in domains:
            logger.info(f"Updating translations for {domain}")
            locale_folder_setup(domain)
            _rebuild(domain)
            _sync(domain)
    else:
        logger.error("Not able to find i18ndude")
