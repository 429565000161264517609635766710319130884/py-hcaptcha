from .curves import gen_mouse_move
from .agents import Agent, random_agent
from .structures import Pe, FakeTime
from .utils import gen_widget_id
try:
    from xrequests import HttpClient
except ImportError:
    from requests import Session as HttpClient
from PIL import Image
from io import BytesIO
from urllib.parse import urlencode
import random
import json

FRAME_SIZE = (400, 600)
TASKS_PER_PAGE = 9
TASKS_PER_ROW = 3
TASK_IMAGE_SIZE = (123, 123)
TASK_IMAGE_START_POS = (11, 130)
TASK_IMAGE_PADDING = (5, 6)
VERIFY_BTN_POS = (314, 559)

class Challenge:
    base_url = "https://hcaptcha.com"

    def __init__(self, sitekey, host,
                 version=None, invisible=None, widget_id=None,
                 agent=None, http_client=None):
        version = version if version is not None else "c4ed6d3"
        invisible = invisible if invisible is not None else False
        widget_id = widget_id or gen_widget_id()
        agent = agent if agent is not None else random_agent()
        http_client = http_client if http_client is not None else HttpClient()

        self.host = host
        self.sitekey = sitekey
        self.http_client = http_client
        self.agent = agent

        self._version = version
        self._invisible = invisible
        self._widget_id = widget_id

        self._time = FakeTime()
        # TODO: add mouse movements for top
        self._top = Pe(self._time)
        self._frame = Pe(self._time)

        self._set_state()
        self._get_captcha()
        self._frame.set_data("dct", self._frame._manifest["st"])

    def tasks(self, with_image=True, only=None):
        for task in self._tasklist:
            if only and not task["task_key"] in only:
                continue
            if with_image:
                resp = self.http_client.request("GET", task["datapoint_uri"])
                image = Image.open(BytesIO(resp.content))
                yield (task["task_key"], image)
            else:
                yield (task["task_key"], task["datapoint_uri"])

    def solve(self, answers):
        self._simulate_solve(answers)
        
        resp = self.http_client.request(
            method="POST",
            url=f"{self.base_url}/checkcaptcha/{self._key}?s={self.sitekey}",
            headers={
                "Connection": "keep-alive",
                #"sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
                "Accept": "*/*",
                #"sec-ch-ua-mobile": "?0",
                "User-Agent": self.agent.user_agent,
                "Content-type": "application/json;charset=UTF-8",
                "Origin": "https://newassets.hcaptcha.com",
                #"Sec-Fetch-Site": "same-site",
                #"Sec-Fetch-Mode": "cors",
                #"Sec-Fetch-Dest": "empty",
                "Referer": "https://newassets.hcaptcha.com/",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9"
            },
            data=json.dumps({
                "answers": {
                    task["task_key"]: "true" if task["task_key"] in answers else "false"
                    for task in self._tasklist
                },
                "c": "null",
                "job_mode": self.type,
                "motionData": json.dumps({
                    **self._frame.get_data(),
                    "v": 1,
                    "topLevel": self._top.get_data()
                }, separators=(",", ":")),
                "n": None,
                "serverdomain": self.host,
                "sitekey": self.sitekey,
                "v": self._version
            }, separators=(",", ":"))
        )
        
        data = resp.json()
        if data.get("pass"):
            return data["generated_pass_UUID"]

    def _set_state(self):
        self._top.record()
        self._time.sleep(random.uniform(1, 2))
        self._frame.record()
        self._top.set_data("sc", {
            "availWidth": self.agent.avail_width,
            "availHeight": self.agent.avail_height,
            "width": self.agent.width,
            "height": self.agent.height,
            "colorDepth": self.agent.color_depth,
            "pixelDepth": self.agent.pixel_depth,
            "availLeft": 0,
            "availTop": 0
        })
        self._top.set_data("nv", {
            "vendorSub": self.agent.vendor_sub,
            "productSub": self.agent.product_sub,
            "vendor": self.agent.vendor,
            "maxTouchPoints": self.agent.max_touch_points,
            "userActivation": {},
            "doNotTrack": self.agent.do_not_track,
            "geolocation": {},
            "connection": {},
            "webkitTemporaryStorage": {},
            "webkitPersistentStorage": {},
            "hardwareConcurrency": self.agent.hardware_concurrency,
            "cookieEnabled": True,
            "appCodeName": self.agent.app_code_name,
            "appName": self.agent.app_name,
            "appVersion": self.agent.app_version,
            "platform": self.agent.platform,
            "product": self.agent.product,
            "userAgent": self.agent.user_agent,
            "language": self.agent.language,
            "languages": self.agent.languages,
            "onLine": self.agent.on_line,
            "webdriver": self.agent.webdriver,
            "serial": {},
            "scheduling": {},
            "mediaCapabilities": {},
            "permissions": {},
            "locks": {},
            "wakeLock": {},
            "usb": {},
            "mediaSession": {},
            "clipboard": {},
            "credentials": {},
            "keyboard": {},
            "mediaDevices": {},
            "storage": {},
            "serviceWorker": {},
            "deviceMemory": self.agent.device_memory,
            "hid": {},
            "presentation": {},
            "userAgentData": {},
            "bluetooth": {},
            "xr": {},
            "plugins": self.agent.plugins
        })
        self._top.set_data("dr", "")
        self._top.set_data("inv", False)
        self._top.set_data("exec", False)
        self._top.circ_buff_push("wn", [
            2844,
            1478,
            1, # devicePixelRatio
            self._time.ms_time()
        ])
        self._top.circ_buff_push("xy", [
            0, # scrollX
            0, # scrollY
            1, # document.documentElement.clientWidth / window.innerWidth
            self._time.ms_time()
        ])

    def _get_captcha(self):
        resp = self.http_client.request(
            method="POST",
            url=f"{self.base_url}/getcaptcha?s={self.sitekey}",
            headers={
                "Connection": "keep-alive",
                #"sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
                "Accept": "application/json",
                #"sec-ch-ua-mobile": "?0",
                "User-Agent": self.agent.user_agent,
                "Content-type": "application/x-www-form-urlencoded",
                "Origin": "https://newassets.hcaptcha.com",
                #"Sec-Fetch-Site": "same-site",
                #"Sec-Fetch-Mode": "cors",
                #"Sec-Fetch-Dest": "empty",
                "Referer": "https://newassets.hcaptcha.com/",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9"
            },
            data=urlencode({
                "v": self._version,
                "sitekey": self.sitekey,
                "host": self.host,
                "hl": "en",
                "motionData": json.dumps({
                    **self._frame.get_data(),
                    "v": 1,
                    "topLevel": self._top.get_data(),
                    "session": [],
                    "widgetList": [self._widget_id],
                    "widgetId": self._widget_id,
                    "href": f"https://{self.host}/",
                    "prev": {
                        "escaped": False,
                        "passed": False,
                        "expiredChallenge": False,
                        "expiredResponse": False
                    }
                }, separators=(",", ":"))
            })
        )
        data = resp.json()
        self.type = data["request_type"]
        self.question = data["requester_question"]["en"]
        self._key = data["key"]
        self._config = data["request_config"]
        self._tasklist = data["tasklist"]

    def _simulate_solve(self, answers):
        total_pages = int(len(self._tasklist)/TASKS_PER_PAGE)
        cursor_pos = (
            random.randint(1, 5),
            random.randint(300, 350)
        )

        for page in range(total_pages):
            page_tasks = self._tasklist[page*TASKS_PER_PAGE:(page+1)*TASKS_PER_PAGE]
            for task_index, task in enumerate(page_tasks):
                if not task["task_key"] in answers:
                    continue
                task_pos = (
                    (TASK_IMAGE_SIZE[0] * int(task_index % TASKS_PER_ROW))
                        + TASK_IMAGE_PADDING[0] * int(task_index % TASKS_PER_ROW)
                        + random.randint(10, TASK_IMAGE_SIZE[0])
                        + TASK_IMAGE_START_POS[0],
                    (TASK_IMAGE_SIZE[1] * int(task_index / TASKS_PER_ROW))
                        + TASK_IMAGE_PADDING[1] * int(task_index / TASKS_PER_ROW)
                        + random.randint(10, TASK_IMAGE_SIZE[1])
                        + TASK_IMAGE_START_POS[1],
                )
                for event in gen_mouse_move(cursor_pos, task_pos, self._time,
                        offsetBoundaryX=0, offsetBoundaryY=0, leftBoundary=0,
                        rightBoundary=FRAME_SIZE[0], upBoundary=FRAME_SIZE[1],
                        downBoundary=0):
                    self._frame.record_event("mm", event)
                # TODO: add time delay for mouse down and mouse up
                self._frame.record_event("md", event)
                self._frame.record_event("mu", event)
                cursor_pos = task_pos
            
            # click verify/next/skip btn
            btn_pos = (
                VERIFY_BTN_POS[0] + random.randint(5, 50),
                VERIFY_BTN_POS[1] + random.randint(5, 15),
            )
            for event in gen_mouse_move(cursor_pos, btn_pos, self._time,
                        offsetBoundaryX=0, offsetBoundaryY=0, leftBoundary=0,
                        rightBoundary=FRAME_SIZE[0], upBoundary=FRAME_SIZE[1],
                        downBoundary=0):
                self._frame.record_event("mm", event)
            # TODO: add time delay for mouse down and mouse up
            self._frame.record_event("md", event)
            self._frame.record_event("mu", event)
            cursor_pos = btn_pos
