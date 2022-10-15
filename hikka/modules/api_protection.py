#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import asyncio
import io
import json
import logging
import time

from telethon.tl.types import Message
from telethon.tl import functions
from telethon.tl.tlobject import TLRequest

from .. import loader, utils
from ..inline.types import InlineCall

logger = logging.getLogger(__name__)

GROUPS = [
    "auth",
    "account",
    "users",
    "contacts",
    "messages",
    "updates",
    "photos",
    "upload",
    "help",
    "channels",
    "bots",
    "payments",
    "stickers",
    "phone",
    "langpack",
    "folders",
    "stats",
]


def decapitalize(string: str) -> str:
    return string[0].lower() + string[1:]


CONSTRUCTORS = {
    decapitalize(
        method.__class__.__name__.rsplit("Request", 1)[0]
    ): method.CONSTRUCTOR_ID
    for method in utils.array_sum(
        [
            [
                method
                for method in dir(getattr(functions, group))
                if isinstance(method, TLRequest)
            ]
            for group in GROUPS
        ]
    )
}


@loader.tds
class APIRatelimiterMod(loader.Module):
    """Helps userbot avoid spamming Telegram API"""

    strings = {
        "name": "APILimiter",
        "warning": (
            "<emoji document_id=6319093650693293883>☣️</emoji>"
            " <b>WARNING!</b>\n\nYour account exceeded the limit of requests, specified"
            " in config. In order to prevent Telegram API Flood, userbot has been"
            " <b>fully frozen</b> for {} seconds. Further info is provided in attached"
            " file. \n\nIt is recommended to get help in <code>{prefix}support</code>"
            " group!\n\nIf you think, that it is an intended behavior, then wait until"
            " userbot gets unlocked and next time, when you will be going to perform"
            " such an operation, use <code>{prefix}suspend_api_protect</code> &lt;time"
            " in seconds&gt;"
        ),
        "args_invalid": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>Invalid arguments</b>"
        ),
        "suspended_for": (
            "<emoji document_id=5458450833857322148>👌</emoji> <b>API Flood Protection"
            " is disabled for {} seconds</b>"
        ),
        "test": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>This action will"
            " expose your account to flooding Telegram API.</b> <i>In order to confirm,"
            " that you really know, what you are doing, complete this simple test -"
            " find the emoji, differing from others</i>"
        ),
        "on": (
            "<emoji document_id=5458450833857322148>👌</emoji> <b>Protection enabled</b>"
        ),
        "off": (
            "<emoji document_id=5458450833857322148>👌</emoji> <b>Protection"
            " disabled</b>"
        ),
        "u_sure": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>Are you sure?</b>"
        ),
        "_cfg_time_sample": "Time sample through which the bot will count requests",
        "_cfg_threshold": "Threshold of requests to trigger protection",
        "_cfg_local_floodwait": (
            "Freeze userbot for this amount of time, if request limit exceeds"
        ),
        "_cfg_forbidden_methods": (
            "Forbid specified methods from being executed throughout external modules"
        ),
        "btn_no": "🚫 No",
        "btn_yes": "✅ Yes",
    }

    strings_ru = {
        "warning": (
            "<emoji document_id=6319093650693293883>☣️</emoji>"
            " <b>ВНИМАНИЕ!</b>\n\nАккаунт вышел за лимиты запросов, указанные в"
            " конфиге. С целью предотвращения флуда Telegram API, юзербот был"
            " <b>полностью заморожен</b> на {} секунд. Дополнительная информация"
            " прикреплена в файле ниже. \n\nРекомендуется обратиться за помощью в"
            " <code>{prefix}support</code> группу!\n\nЕсли ты считаешь, что это"
            " запланированное поведение юзербота, просто подожди, пока закончится"
            " таймер и в следующий раз, когда запланируешь выполнять такую"
            " ресурсозатратную операцию, используй"
            " <code>{prefix}suspend_api_protect</code> &lt;время в секундах&gt;"
        ),
        "args_invalid": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>Неверные"
            " аргументы</b>"
        ),
        "suspended_for": (
            "<emoji document_id=5458450833857322148>👌</emoji> <b>Защита API отключена"
            " на {} секунд</b>"
        ),
        "test": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>Это действие"
            " открывает юзерботу возможность флудить Telegram API.</b> <i>Для того,"
            " чтобы убедиться, что ты действительно уверен в том, что делаешь - реши"
            " простенький тест - найди отличающийся эмодзи.</i>"
        ),
        "on": "<emoji document_id=5458450833857322148>👌</emoji> <b>Защита включена</b>",
        "off": (
            "<emoji document_id=5458450833857322148>👌</emoji> <b>Защита отключена</b>"
        ),
        "u_sure": "<emoji document_id=6319093650693293883>☣️</emoji> <b>Ты уверен?</b>",
        "_cfg_time_sample": (
            "Временной промежуток, по которому будет считаться количество запросов"
        ),
        "_cfg_threshold": "Порог запросов, при котором будет срабатывать защита",
        "_cfg_local_floodwait": (
            "Заморозить юзербота на это количество секунд, если лимит запросов превышен"
        ),
        "_cfg_forbidden_methods": (
            "Запретить выполнение указанных методов во всех внешних модулях"
        ),
        "btn_no": "🚫 Нет",
        "btn_yes": "✅ Да",
    }

    strings_de = {
        "warning": (
            "<emoji document_id=6319093650693293883>☣️</emoji>"
            " <b>Achtung!</b>\n\nDas Konto hat die in der Konfiguration angegebenen"
            " Grenzwerte für Anfragen überschritten. Um Telegram API-Flooding zu"
            " verhindern, wurde der <b>ganze Userbot</b> für {} Sekunden"
            " eingefroren. Weitere Informationen finden Sie im unten angefügten"
            " Datei.\n\nWir empfehlen Ihnen, sich mit Hilfe der <code>{prefix}"
            "support</code> Gruppe zu helfen!\n\nWenn du denkst, dass dies"
            " geplantes Verhalten des Userbots ist, dann warte einfach, bis der"
            " Timer abläuft und versuche beim nächsten Mal, eine so ressourcen"
            " intensive Operation wie <code>{prefix}suspend_api_protect</code>"
            " &lt;Zeit in Sekunden&gt; zu planen."
        ),
        "args_invalid": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>Ungültige"
            " Argumente</b>"
        ),
        "suspended_for": (
            "<emoji document_id=5458450833857322148>👌</emoji> <b>API Flood"
            " Protection ist für {} Sekunden deaktiviert</b>"
        ),
        "test": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>Dieser"
            " Vorgang wird deinen Account ermöglichen, die Telegram API zu"
            " überfluten.</b> <i>Um sicherzustellen, dass du wirklich weißt, was"
            " du tust, beende diesen einfachen Test - findest du das Emoji, das von"
            " den anderen abweicht?</i>"
        ),
        "on": (
            "<emoji document_id=5458450833857322148>👌</emoji> <b>Schutz aktiviert</b>"
        ),
        "off": (
            "<emoji document_id=5458450833857322148>👌</emoji> <b>Schutz deaktiviert</b>"
        ),
        "u_sure": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>Bist du sicher?</b>"
        ),
        "_cfg_time_sample": "Zeitintervall, in dem die Anfragen gezählt werden",
        "_cfg_threshold": (
            "Schwellenwert für Anfragen, ab dem der Schutz aktiviert wird"
        ),
        "_cfg_local_floodwait": (
            "Einfrieren des Userbots für diese Anzahl von Sekunden, wenn der Grenzwert"
            " überschritten wird"
        ),
        "_cfg_forbidden_methods": "Verbotene Methoden in allen externen Modulen",
        "btn_no": "🚫 Nein",
        "btn_yes": "✅ Ja",
    }

    strings_tr = {
        "warning": (
            "<emoji document_id=6319093650693293883>☣️</emoji>"
            " <b>Dikkat!</b>\n\nHesap yapılandırmasında belirtilen sınır değerlerini"
            " aştı. Telegram API sızmalarını önlemek için <b>tüm userbot</b>"
            " {} saniye boyunca donduruldu. Daha fazla bilgi için aşağıda eklenen"
            " dosyayı okuyun.\n\n<code>{prefix}support</code> grubunu kullanarak"
            " yardıma ihtiyacınız olursa lütfen yardım alın!\n\nEğer"
            " bu işlem userbotun planlı davranışı ise, zamanlayıcı süresini bekleyin"
            " ve böyle bir yüksek kaynak tüketimi gerektiren işlemi"
            " <code>{prefix}suspend_api_protect</code> &lt;saniye&gt;"
            " ile planlayın."
        ),
        "args_invalid": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>Geçersiz"
            " argümanlar</b>"
        ),
        "suspended_for": (
            "<emoji document_id=5458450833857322148>👌</emoji> <b>API Flood koruması"
            " {} saniye için devre dışı bırakıldı</b>"
        ),
        "test": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>Bu işlem"
            " Telegram API'sini sızmaya izin verecektir.</b> <i>Ne yaptığınızdan"
            " emin olmak için basit bir testi çözmek için, farklı olan emojiyi"
            " bulabilir misiniz?</i>"
        ),
        "on": "<emoji document_id=5458450833857322148>👌</emoji> <b>Koruma etkin</b>",
        "off": (
            "<emoji document_id=5458450833857322148>👌</emoji> <b>Koruma devre dışı</b>"
        ),
        "u_sure": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>Emin misin?</b>"
        ),
        "_cfg_time_sample": "Saniyede sayılan isteklerin zaman aralığı",
        "_cfg_threshold": "Koruma etkinleşecek sınır değeri",
        "_cfg_local_floodwait": (
            "Sınır değeri aşıldığında userbotun bu saniye sayısı kadar dondurulması"
        ),
        "_cfg_forbidden_methods": "Tüm harici modüllerde yasaklanan yöntemler",
        "btn_no": "🚫 Hayır",
        "btn_yes": "✅ Evet",
    }

    strings_hi = {
        "warning": (
            "<emoji document_id=6319093650693293883>☣️</emoji>"
            " <b>चेतावनी!</b>\n\nइस खाते के लिए विन्यास में निर्दिष्ट सीमा सीमा"
            " पार कर गए हैं। टेलीग्राम एपीआई फ्लडिंग को रोकने के लिए, यह"
            " <b>सभी userbot</b> को {} सेकंड तक जमा कर दिया गया है। अधिक"
            " जानकारी के लिए नीचे दिए गए फ़ाइल पढ़ें।\n\nअपनी सहायता के लिए"
            " <code>{prefix}support</code> समूह का उपयोग करें!\n\nयदि आपको लगता है"
            " यह उपयोगकर्ता बॉट की योजित व्यवहार है, तो बस टाइमर समाप्त होने"
            " तक इंतजार करें और अगली बार एक ऐसी संसाधन ज्यादा खर्च करने वाली"
            " ऑपरेशन को योजित करने के लिए <code>{prefix}suspend_api_protect</code>"
            " &lt;सेकंड&gt; का उपयोग करें।"
        ),
        "args_invalid": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>अमान्य तर्क</b>"
        ),
        "suspended_for": (
            "<emoji document_id=5458450833857322148>👌</emoji> <b>API Flood"
            " सुरक्षा को {} सेकंड के लिए अक्षम कर दिया गया है</b>"
        ),
        "test": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>यह ऑपरेशन"
            " टेलीग्राम एपीआई को फ्लड करने की अनुमति देगा।</b> <i>आप क्या कर रहे हैं"
            " यह सुनिश्चित करने के लिए एक आसान परीक्षण को हल करें, जिसमें अलग"
            " एमोजी का पता लगाएं?</i>"
        ),
        "on": "<emoji document_id=5458450833857322148>👌</emoji> <b>सुरक्षा सक्षम</b>",
        "off": "<emoji document_id=5458450833857322148>👌</emoji> <b>सुरक्षा अक्षम</b>",
        "u_sure": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>क्या आप"
            " सुनिश्चित हैं?</b>"
        ),
        "_cfg_time_sample": "प्रति सेकंड गिने जाने वाले अनुरोधों की समय सीमा",
        "_cfg_threshold": "सुरक्षा सक्षम करने के लिए मान सीमित करें",
        "_cfg_local_floodwait": (
            "यूजरबॉट को इस संख्या के सेकंड के लिए फ्रीज करें जब सीमा मान पार हो जाए"
        ),
        "_cfg_forbidden_methods": "सभी बाहरी मॉड्यूल में निषिद्ध तरीके",
        "btn_no": "🚫 नहीं",
        "btn_yes": "✅ हाँ",
    }

    strings_uz = {
        "warning": (
            "<emoji document_id=6319093650693293883>☣️</emoji>"
            " <b>Ogohlantirish!</b>\n\nBu hisob uchun konfiguratsiyada ko'rsatilgan"
            " chegaralar chegarani o'zgartirgan.\n\nTelegram API Flood"
            " to'xtatish uchun, bu <b>hammasi userbot</b> uchun {} sekundni"
            " blokirovka qilindi. Batafsil ma'lumot uchun pastdagi faylni o'qing.\n\n"
            "Yordam uchun <code>{prefix}support</code> guruhidan foydalaning!\n\nAgar"
            " siz hisobni botning yordamchisi bo'lishi kerak bo'lgan amalni bajarishga"
            " imkoniyat berishga o'xshaysiz, unda faqat blokirovkani to'xtatish uchun"
            " <code>{prefix}suspend_api_protect</code> &lt;sekund&gt; dan foydalaning."
        ),
        "args_invalid": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>Noto'g'ri"
            " argument</b>"
        ),
        "suspended_for": (
            "<emoji document_id=5458450833857322148>👌</emoji> <b>API Flood"
            " himoya {} sekund uchun to'xtatildi</b>"
        ),
        "test": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>Ushbu amal Telegram"
            " API-ni flood qilishga ruxsat beradi.</b> <i>Siz qanday ish"
            " bajarayotganingizni tekshirish uchun oson testni bajarishga harakat"
            " qiling, emojilarni aniqlash uchun?</i>"
        ),
        "on": "<emoji document_id=5458450833857322148>👌</emoji> <b>Himoya yoqildi</b>",
        "off": (
            "<emoji document_id=5458450833857322148>👌</emoji> <b>Himoya o'chirildi</b>"
        ),
        "u_sure": (
            "<emoji document_id=6319093650693293883>☣️</emoji> <b>Siz"
            " ishonchingiz komilmi?</b>"
        ),
        "_cfg_time_sample": "Sekundda qabul qilinadigan so'rovlar soni chegarasi",
        "_cfg_threshold": "Himoya yoqish uchun qiymatni chegaralash",
        "_cfg_local_floodwait": (
            "Foydalanuvchi botni ushbu soniya davomida blokirovka qiladi, agar"
            " chegaralar qiymati oshsa"
        ),
        "_cfg_forbidden_methods": "Barcha tashqi modullarda taqiqlangan usullar",
        "btn_no": "🚫 Yo'q",
        "btn_yes": "✅ Ha",
    }

    _ratelimiter = []
    _suspend_until = 0
    _lock = False

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "time_sample",
                15,
                lambda: self.strings("_cfg_time_sample"),
                validator=loader.validators.Integer(minimum=1),
            ),
            loader.ConfigValue(
                "threshold",
                100,
                lambda: self.strings("_cfg_threshold"),
                validator=loader.validators.Integer(minimum=10),
            ),
            loader.ConfigValue(
                "local_floodwait",
                30,
                lambda: self.strings("_cfg_local_floodwait"),
                validator=loader.validators.Integer(minimum=10, maximum=3600),
            ),
            loader.ConfigValue(
                "forbidden_methods",
                ["joinChannel", "importChatInvite"],
                lambda: self.strings("_cfg_forbidden_methods"),
                validator=loader.validators.MultiChoice(
                    [
                        "sendReaction",
                        "joinChannel",
                        "importChatInvite",
                    ]
                ),
                on_change=lambda: self._client.forbid_constructors(
                    map(
                        lambda x: CONSTRUCTORS[x], self.config["forbidden_constructors"]
                    )
                ),
            ),
        )

    async def client_ready(self):
        asyncio.ensure_future(self._install_protection())

    async def _install_protection(self):
        await asyncio.sleep(30)  # Restart lock
        if hasattr(self._client._call, "_old_call_rewritten"):
            raise loader.SelfUnload("Already installed")

        old_call = self._client._call

        async def new_call(
            sender: "MTProtoSender",  # type: ignore
            request: "TLRequest",  # type: ignore
            ordered: bool = False,
            flood_sleep_threshold: int = None,
        ):
            if time.perf_counter() > self._suspend_until and not self.get(
                "disable_protection",
                True,
            ):
                request_name = type(request).__name__
                self._ratelimiter += [[request_name, time.perf_counter()]]

                self._ratelimiter = list(
                    filter(
                        lambda x: time.perf_counter() - x[1]
                        < int(self.config["time_sample"]),
                        self._ratelimiter,
                    )
                )

                if (
                    len(self._ratelimiter) > int(self.config["threshold"])
                    and not self._lock
                ):
                    self._lock = True
                    report = io.BytesIO(
                        json.dumps(
                            self._ratelimiter,
                            indent=4,
                        ).encode("utf-8")
                    )
                    report.name = "local_fw_report.json"

                    await self.inline.bot.send_document(
                        self.tg_id,
                        report,
                        caption=self.strings("warning").format(
                            self.config["local_floodwait"],
                            prefix=self.get_prefix(),
                        ),
                    )

                    # It is intented to use time.sleep instead of asyncio.sleep
                    time.sleep(int(self.config["local_floodwait"]))
                    self._lock = False

            return await old_call(sender, request, ordered, flood_sleep_threshold)

        self._client._call = new_call
        self._client._old_call_rewritten = old_call
        self._client._call._hikka_overwritten = True
        logger.debug("Successfully installed ratelimiter")

    async def on_unload(self):
        if hasattr(self._client, "_old_call_rewritten"):
            self._client._call = self._client._old_call_rewritten
            delattr(self._client, "_old_call_rewritten")
            logger.debug("Successfully uninstalled ratelimiter")

    @loader.command(
        ru_doc="<время в секундах> - Заморозить защиту API на N секунд",
        de_doc="<Sekunden> - API-Schutz für N Sekunden einfrieren",
        tr_doc="<saniye> - API korumasını N saniye dondur",
        hi_doc="<सेकंड> - API सुरक्षा को N सेकंड जमा करें",
        uz_doc="<soniya> - API himoyasini N soniya o'zgartirish",
    )
    async def suspend_api_protect(self, message: Message):
        """<time in seconds> - Suspend API Ratelimiter for n seconds"""
        args = utils.get_args_raw(message)

        if not args or not args.isdigit():
            await utils.answer(message, self.strings("args_invalid"))
            return

        self._suspend_until = time.perf_counter() + int(args)
        await utils.answer(message, self.strings("suspended_for").format(args))

    @loader.command(
        ru_doc="Включить/выключить защиту API",
        de_doc="API-Schutz einschalten / ausschalten",
        tr_doc="API korumasını aç / kapat",
        hi_doc="API सुरक्षा चालू / बंद करें",
        uz_doc="API himoyasini yoqish / o'chirish",
    )
    async def api_fw_protection(self, message: Message):
        """Toggle API Ratelimiter"""
        await self.inline.form(
            message=message,
            text=self.strings("u_sure"),
            reply_markup=[
                {"text": self.strings("btn_no"), "action": "close"},
                {"text": self.strings("btn_yes"), "callback": self._finish},
            ],
        )

    async def _finish(self, call: InlineCall):
        state = self.get("disable_protection", True)
        self.set("disable_protection", not state)
        await call.edit(self.strings("on" if state else "off"))
