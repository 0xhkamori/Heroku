# ©️ Dan Gazizullin, 2021-2023
# This file is a part of Hikka Userbot
# 🌐 https://github.com/hikariatama/Hikka
# You can redistribute it and/or modify it under the terms of the GNU AGPLv3
# 🔑 https://www.gnu.org/licenses/agpl-3.0.html

import asyncio
import base64
import logging
import random
import re
import typing

import requests
import rsa
from hikkatl.tl.types import Message
from hikkatl.utils import resolve_inline_message_id

from .. import loader, translations, utils
from ..types import InlineCall

logger = logging.getLogger(__name__)

pubkey = rsa.PublicKey(
    7110455561671499155469672749235101198284219627796886527432331759773809536504953770286294224729310191037878347906574131955439231159825047868272932664151403,
    65537,
)

REGEXES = [
    re.compile(
        r"https:\/\/github\.com\/([^\/]+?)\/([^\/]+?)\/raw\/(?:main|master)\/([^\/]+\.py)"
    ),
    re.compile(
        r"https:\/\/raw\.githubusercontent\.com\/([^\/]+?)\/([^\/]+?)\/(?:main|master)\/([^\/]+\.py)"
    ),
]


@loader.tds
class UnitHeta(loader.Module):
    """Gives @hikkamods_bot a right to download modules from official modules aggregator and autoupdate them"""

    e = "<emoji document_id=5210952531676504517>❌</emoji>"

    strings = {
        "name": "UnitHeta",
        "no_query": f"{e} <b>You must specify query</b>",
        "no_results": f"{e} <b>No results</b>",
        "api_error": f"{e} <b>API is having issues</b>",
        "result": (
            "🥰 <b>Results for</b> <code>{query}</code><b>:</b>\n\n🧳 <code>{name}</code>"
            " <b>by</b> <code>{dev}</code>\n👨‍🏫 <i>{cls_doc}</i>\n\n📚"
            " <b>Commands:</b>\n{commands}\n\n🔗 <b>Install:</b> <code>{prefix}dlm"
            " {link}</code>"
        ),
        "install": "🪄 Install",
        "loaded": "✅ <b>Sucessfully installed</b>",
        "not_loaded": "❌ <b>Installation failed</b>",
        "language": "en",
    }

    strings_ru = {
        "no_query": f"{e} <b>Вы должны указать запрос</b>",
        "no_results": f"{e} <b>Нет результатов</b>",
        "api_error": f"{e} <b>С API случилась беда</b>",
        "result": (
            "🥰 <b>Результаты для</b> <code>{query}</code><b>:</b>\n\n🧳"
            " <code>{name}</code> <b>от</b> <code>{dev}</code>\n👨‍🏫"
            " <i>{cls_doc}</i>\n\n📚 <b>Команды:</b>\n{commands}\n\n🔗 <b>Установить:</b>"
            " <code>{prefix}dlm {link}</code>"
        ),
        "install": "🪄 Установить",
        "loaded": "✅ <b>Успешно установлено</b>",
        "not_loaded": "❌ <b>Установка не удалась</b>",
        "language": "ru",
    }

    strings_es = {
        "no_query": f"{e} <b>Debes especificar una consulta</b>",
        "no_results": f"{e} <b>No hay resultados</b>",
        "api_error": f"{e} <b>Hay problemas con la API</b>",
        "result": (
            "🥰 <b>Resultados para</b> <code>{query}</code><b>:</b>\n\n🧳"
            " <code>{name}</code> <b>por</b> <code>{dev}</code>\n👨‍🏫"
            " <i>{cls_doc}</i>\n\n📚 <b>Comandos:</b>\n{commands}\n\n🔗 <b>Instalar:</b>"
            " <code>{prefix}dlm {link}</code>"
        ),
        "install": "🪄 Instalar",
        "loaded": "✅ <b>Instalado con éxito</b>",
        "not_loaded": "❌ <b>La instalación falló</b>",
        "language": "es",
    }

    strings_de = {
        "no_query": f"{e} <b>Du musst eine Abfrage angeben</b>",
        "no_results": f"{e} <b>Keine Ergebnisse</b>",
        "api_error": f"{e} <b>Es gibt Probleme mit der API</b>",
        "result": (
            "🥰 <b>Ergebnisse für</b> <code>{query}</code><b>:</b>\n\n🧳"
            " <code>{name}</code> <b>von</b> <code>{dev}</code>\n👨‍🏫"
            " <i>{cls_doc}</i>\n\n📚 <b>Befehle:</b>\n{commands}\n\n🔗"
            " <b>Installieren:</b> <code>{prefix}dlm {link}</code>"
        ),
        "install": "🪄 Installieren",
        "loaded": "✅ <b>Erfolgreich installiert</b>",
        "not_loaded": "❌ <b>Die Installation ist fehlgeschlagen</b>",
        "language": "de",
    }

    strings_fr = {
        "no_query": f"{e} <b>Vous devez spécifier une requête</b>",
        "no_results": f"{e} <b>Aucun résultat</b>",
        "api_error": f"{e} <b>Quelque chose s'est mal passé avec l'API</b>",
        "result": (
            "🥰 <b>Résultats pour</b> <code>{query}</code><b>:</b>\n\n🧳"
            " <code>{name}</code> <b>par</b> <code>{dev}</code>\n👨‍🏫"
            " <i>{cls_doc}</i>\n\n📚 <b>Commandes:</b>\n{commands}\n\n🔗"
            " <b>Installer:</b> <code>{prefix}dlm {link}</code>"
        ),
        "install": "🪄 Installer",
        "loaded": "✅ <b>Installation réussie</b>",
        "not_loaded": "❌ <b>Installation échouée</b>",
        "language": "fr",
    }

    strings_uz = {
        "no_query": f"{e} <b>Siz so'rovni belgilamadingiz</b>",
        "no_results": f"{e} <b>Natija topilmadi</b>",
        "api_error": f"{e} <b>API bilan muammo yuz berdi</b>",
        "result": (
            "🥰 <b>Ushbu</b> <code>{query}</code><b>uchun natijalar:</b>\n\n🧳"
            " <code>{name}</code> <b>to'g'risida</b> <code>{dev}</code>\n👨‍🏫"
            " <i>{cls_doc}</i>\n\n📚 <b>Komandalar:</b>\n{commands}\n\n🔗"
            " <b>O'rnatish:</b> <code>{prefix}dlm {link}</code>"
        ),
        "install": "🪄 O'rnatish",
        "loaded": "✅ <b>Muvaffaqiyatli o'rnatildi</b>",
        "not_loaded": "❌ <b>O'rnatish muvaffaqiyatsiz bo'ldi</b>",
        "language": "uz",
    }

    strings_tr = {
        "no_query": f"{e} <b>Bir sorgu belirtmelisiniz</b>",
        "no_results": f"{e} <b>Sonuç yok</b>",
        "api_error": f"{e} <b>API ile ilgili bir sorun oluştu</b>",
        "result": (
            "🥰 <b>Sonuçlar için</b> <code>{query}</code><b>:</b>\n\n🧳"
            " <code>{name}</code> <b>geliştirici</b> <code>{dev}</code>\n👨‍🏫"
            " <i>{cls_doc}</i>\n\n📚 <b>Komutlar:</b>\n{commands}\n\n🔗 <b>Yükle:</b>"
            " <code>{prefix}dlm {link}</code>"
        ),
        "install": "🪄 Yükle",
        "loaded": "✅ <b>Başarıyla yüklendi</b>",
        "not_loaded": "❌ <b>Yükleme başarısız oldu</b>",
        "language": "tr",
    }

    strings_it = {
        "no_query": f"{e} <b>Devi specificare una query</b>",
        "no_results": f"{e} <b>Nessun risultato</b>",
        "api_error": f"{e} <b>Si è verificato un'errore con l'API</b>",
        "result": (
            "🥰 <b>Risultati per</b> <code>{query}</code><b>:</b>\n\n🧳"
            " <code>{name}</code> <b>da</b> <code>{dev}</code>\n👨‍🏫"
            " <i>{cls_doc}</i>\n\n📚 <b>Comandi:</b>\n{commands}\n\n🔗 <b>Installare:</b>"
            " <code>{prefix}dlm {link}</code>"
        ),
        "install": "🪄 Installare",
        "loaded": "✅ <b>Installazione riuscita</b>",
        "not_loaded": "❌ <b>Installazione non riuscita</b>",
        "language": "it",
    }

    strings_kk = {
        "no_query": f"{e} <b>Сұранымды көрсетуіңіз керек</b>",
        "no_results": f"{e} <b>Нәтижелер жоқ</b>",
        "api_error": f"{e} <b>API-ға қате кетті</b>",
        "result": (
            "🥰 <b>Сұранымдың нәтижелері</b> <code>{query}</code><b>:</b>\n\n🧳"
            " <code>{name}</code> <b>төлесін</b> <code>{dev}</code>\n👨‍🏫"
            " <i>{cls_doc}</i>\n\n📚 <b>Командалар:</b>\n{commands}\n\n🔗 <b>Орнату:</b>"
            " <code>{prefix}dlm {link}</code>"
        ),
        "install": "🪄 Орнату",
        "loaded": "✅ <b>Орнату сәтті аяқталды</b>",
        "not_loaded": "❌ <b>Орнату сәтсіз аяқталды</b>",
        "language": "kk",
    }

    strings_tt = {
        "no_query": f"{e} <b>Зиндергә мәгълүматләр кертмәгәнсез</b>",
        "no_results": f"{e} <b>Нәтиҗәләр табылмады</b>",
        "api_error": f"{e} <b>API-сәхифәсе белән хата</b>",
        "result": (
            "🥰 <b>Зиндергә нәтиҗәләр</b> <code>{query}</code><b>:</b>\n\n🧳"
            " <code>{name}</code> <b>төзәтелгән</b> <code>{dev}</code>\n👨‍🏫"
            " <i>{cls_doc}</i>\n\n📚 <b>Командалар:</b>\n{commands}\n\n🔗"
            " <b>Установить:</b> <code>{prefix}dlm {link}</code>"
        ),
        "install": "🪄 Установить",
        "loaded": "✅ <b>Установка уңышлы тамамланды</b>",
        "not_loaded": "❌ <b>Установка үтәлмәде</b>",
        "language": "tt",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "autoupdate",
                False,
                (
                    "Do you want to autoupdate modules? (Join @heta_updates in order"
                    " for this option to take effect) ⚠️ Use at your own risk!"
                ),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "translate",
                True,
                (
                    "Do you want to translate module descriptions and command docs to"
                    " the language, specified in Hikka? (This option is experimental,"
                    " and might not work properly)"
                ),
                validator=loader.validators.Boolean(),
            ),
        )

    async def client_ready(self):
        if self.config["autoupdate"]:
            await self.request_join(
                "@heta_updates",
                "This channel is the source of update notifications",
            )

        if self.get("nomute"):
            return

        await utils.dnd(self._client, "@hikkamods_bot", archive=False)
        self.set("nomute", True)

    async def _install(self, call: InlineCall, url: str, text: str):
        await call.edit(
            text,
            reply_markup={
                "text": (
                    self.strings("loaded")
                    if await self._load_module(url)
                    else self.strings("not_loaded")
                ),
                "data": "empty",
            },
        )

    @loader.command(
        ru_doc="<запрос> - Ищет модули в репозитории Heta",
        de_doc="<Anfrage> - Sucht Module im Heta-Repository",
        uz_doc="<so'rov> - Heta ombori uchun modullarni qidiradi",
        tr_doc="<sorgu> - Heta deposunda modülleri arar",
        it_doc="<richiesta> - Cerca moduli nel repository Heta",
        fr_doc="<requête> - Recherche des modules dans le référentiel Heta",
        kk_doc="<сұраным> - Heta орталығында модульларды іздейді",
        tt_doc="<зиндергә> - Heta депозиториясендә модульләрне таба",
        es_doc="<consulta> - Busca módulos en el repositorio Heta",
    )
    async def heta(self, message: Message):
        """<query> - Searches Heta repository for modules"""
        if not (query := utils.get_args_raw(message)):
            await utils.answer(message, self.strings("no_query"))
            return

        if not (
            response := await utils.run_sync(
                requests.get,
                "https://heta.hikariatama.ru/search",
                params={"q": query, "limit": 1},
            )
        ):
            await utils.answer(message, self.strings("no_results"))
            return

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            await utils.answer(message, self.strings("api_error"))
            return

        if not (result := response.json()):
            await utils.answer(message, self.strings("no_results"))
            return

        result = result[0]

        commands = "\n".join(
            [
                f"▫️ <code>{self.get_prefix()}{cmd}</code>:"
                f" <b>{utils.escape_html(cmd_doc)}</b>"
                for cmd, cmd_doc in result["module"]["commands"].items()
            ]
        )

        kwargs = {
            "name": utils.escape_html(result["module"]["name"]),
            "dev": utils.escape_html(result["module"]["dev"]),
            "commands": commands,
            "cls_doc": utils.escape_html(result["module"]["cls_doc"]),
            "link": result["module"]["link"],
            "query": utils.escape_html(query),
            "prefix": self.get_prefix(),
        }

        strings = (
            self.strings._base_strings["result"]
            if self.config["translate"]
            else self.strings("result")
        )

        text = strings.format(**kwargs)

        if len(text) > 4096:
            kwargs["commands"] = "..."
            text = strings.format(**kwargs)

        mark = lambda text: {
            "text": self.strings("install"),
            "callback": self._install,
            "args": (result["module"]["link"], text),
        }

        form = await self.inline.form(
            message=message,
            text=text,
            **(
                {"photo": result["module"]["banner"]}
                if result["module"].get("banner")
                else {}
            ),
            reply_markup=mark(text),
        )

        if not self.config["translate"]:
            return

        message_id, peer, _, _ = resolve_inline_message_id(form.inline_message_id)

        try:
            text = await self._client.translate(
                peer,
                message_id,
                self.strings("language"),
            )
            await form.edit(text=text, reply_markup=mark(text))
        except Exception:
            text = self.strings("result").format(**kwargs)
            await form.edit(text=text, reply_markup=mark(text))

    async def _load_module(
        self,
        url: str,
        message: typing.Optional[Message] = None,
    ) -> bool:
        loader_m = self.lookup("loader")
        await loader_m.download_and_install(url, None)

        if getattr(loader_m, "fully_loaded", False):
            loader_m.update_modules_in_db()

        loaded = any(
            link == url for link in loader_m.get("loaded_modules", {}).values()
        )

        if message:
            if loaded:
                await self._client.inline_query(
                    "@hikkamods_bot",
                    f"#confirm_load {message.raw_text.splitlines()[2].strip()}",
                )
            else:
                await self._client.inline_query(
                    "@hikkamods_bot",
                    f"#confirm_fload {message.raw_text.splitlines()[2].strip()}",
                )

        return loaded

    @loader.watcher("in", "only_messages", chat_id=1688624566, contains="Heta url: ")
    async def update_watcher(self, message: Message):
        url = message.raw_text.split("Heta url: ")[1].strip()
        dev, repo, mod = url.lower().split("hikariatama.ru/")[1].split("/")

        if dev == "hikariatama" and repo == "ftg":
            urls = [f"https://mods.hikariatama.ru/{mod}", url]
            if any(
                getattr(module, "__origin__", None).lower().strip("/") in urls
                for module in self.allmodules.modules
            ):
                await self._load_module(urls[0])
                await asyncio.sleep(random.randint(1, 10))
                await self._client.inline_query(
                    "@hikkamods_bot",
                    f"#confirm_update_noheta {url.split('hikariatama.ru/')[1]}",
                )
                return

        if any(
            getattr(module, "__origin__", "").lower().strip("/")
            == url.lower().strip("/")
            for module in self.allmodules.modules
        ):
            await self._load_module(url)
            await asyncio.sleep(random.randint(1, 10))
            await self._client.inline_query(
                "@hikkamods_bot",
                f"#confirm_update {url.split('hikariatama.ru/')[1]}",
            )
            return

        for module in self.allmodules.modules:
            link = getattr(module, "__origin__", "").lower().strip("/")
            for regex in REGEXES:
                if regex.search(link):
                    dev, repo, mod = regex.search(link).groups()
                    if dev == dev and repo == repo and mod == mod:
                        await self._load_module(link)
                        await asyncio.sleep(random.randint(1, 10))
                        await self._client.inline_query(
                            "@hikkamods_bot",
                            f"#confirm_update_noheta {url.split('hikariatama.ru/')[1]}",
                        )
                        return

    @loader.watcher("in", "only_messages", from_user=5519484330)
    async def watcher(self, message: Message):
        if message.raw_text.startswith("#install"):
            await message.delete()

            fileref = (
                message.raw_text.split("#install:")[1].strip().splitlines()[0].strip()
            )
            sig = base64.b64decode(message.raw_text.splitlines()[1].strip().encode())
            try:
                rsa.verify(
                    rsa.compute_hash(fileref.encode("utf-8"), "SHA-1"), sig, pubkey
                )
            except rsa.pkcs1.VerificationError:
                logger.error("Got message with non-verified signature %s", fileref)
                return

            await self._load_module(f"https://heta.hikariatama.ru/{fileref}", message)
        elif message.raw_text.startswith("#setlang"):
            lang = message.raw_text.split()[1]
            self._db.set(translations.__name__, "lang", lang)
            await self.allmodules.reload_translations()
            await self._client.inline_query("@hikkamods_bot", "#confirm_setlang")
