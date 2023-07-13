from enum import unique
import logging
import voluptuous as vol
import threading, time
import requests
import hashlib
import json

from homeassistant.components.climate import PLATFORM_SCHEMA, ClimateEntity
from homeassistant.components.climate.const import (
    ATTR_HVAC_MODE,
    HVAC_MODE_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_OFF,
    SUPPORT_TARGET_TEMPERATURE,
)

from homeassistant.const import (
    ATTR_TEMPERATURE,
    TEMP_CELSIUS,
)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

global AQARA_REFRESH_TOKEN 
global AQARA_ACCESS_TOKEN
global AQARA_KEYID
global AQARA_APPID
global AQARA_APPKEY


SUPPORT_HVAC = [
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    HVAC_MODE_DRY,
    HVAC_MODE_AUTO,
    HVAC_MODE_OFF,
]

AQARA_MODE_COOL = 0
AQARA_MODE_HEAT = 1
AQARA_MODE_AUTO = 2
AQARA_MODE_FAN_ONLY = 3
AQARA_MODE_DRY = 4


MODE_TO_STATE = {
    AQARA_MODE_COOL: HVAC_MODE_COOL,
    AQARA_MODE_HEAT: HVAC_MODE_HEAT,
    AQARA_MODE_AUTO: HVAC_MODE_AUTO,
    AQARA_MODE_DRY: HVAC_MODE_DRY,
    AQARA_MODE_FAN_ONLY: HVAC_MODE_FAN_ONLY,
}


STATE_TO_MODE = {
    HVAC_MODE_COOL:AQARA_MODE_COOL,
    HVAC_MODE_HEAT:AQARA_MODE_HEAT,
    HVAC_MODE_AUTO:AQARA_MODE_AUTO,
    HVAC_MODE_DRY:AQARA_MODE_DRY,
    HVAC_MODE_FAN_ONLY:AQARA_MODE_FAN_ONLY
}

AC_POWER_ON = 0
AC_POWER_OFF = 1

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required("did"): cv.string,
        vol.Required("accesstoken"): cv.string,
        vol.Required("refreshtoken"): cv.string,
        vol.Required("keyid"): cv.string,
        vol.Required("appid"): cv.string,
        vol.Required("appkey"): cv.string,

    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    global AQARA_REFRESH_TOKEN
    global AQARA_ACCESS_TOKEN
    global AQARA_KEYID
    global AQARA_APPID
    global AQARA_APPKEY
    did = config.get("did")

    AQARA_ACCESS_TOKEN = config.get("accesstoken")
    AQARA_REFRESH_TOKEN = config.get("refreshtoken")
    AQARA_KEYID = config.get("keyid")
    AQARA_APPID = config.get("appid")
    AQARA_APPKEY = config.get("appkey")
    startTimerTask()
    add_entities([AqaraClimate(did)])


TOKEN_FILE_PATH = "/config/tmp/aqara_token.json"


def startTimerTask():
    execTask()
    timer = threading.Timer(518400, startTimerTask)
    timer.start()


def execTask():
    token = getRefreshToken()
    if token is None:
        global AQARA_REFRESH_TOKEN
        token = AQARA_REFRESH_TOKEN
    refreshToken(token)

def sendRequest(jsonData):
    global AQARA_KEYID
    global AQARA_APPID
    global AQARA_APPKEY
    global AQARA_ACCESS_TOKEN
    Appid = AQARA_APPID
    Accesstoken = getAccessToken()
    if Accesstoken is None:
        Accesstoken = AQARA_ACCESS_TOKEN
    Keyid = AQARA_KEYID
    t = time.time()
    TimeNow = int(round(t * 1000))
    Nonce = int(round(t * 1000))
    preSign = "Accesstoken=" + Accesstoken + "&Appid="+Appid + "&Keyid="+Keyid+"&Nonce=" + str(
        Nonce) + "&Time=" + str(TimeNow) + AQARA_APPKEY
    preSign = preSign.lower()
    sign = hashlib.md5(preSign.encode(encoding='utf-8')).hexdigest()
    header = {
        "Appid": Appid,
        "Accesstoken": Accesstoken,
        "Keyid": Keyid,
        "Time": str(TimeNow),
        "Nonce": str(Nonce),
        "Sign": sign,
        "Content-Type": "application/json"
    }
    data = json.dumps(jsonData)
    result = requests.post("https://open-cn.aqara.com/v3.0/open/api", headers=header, data=data)
    return result.json()


def refreshToken(token):
    data = {
        "intent": "config.auth.refreshToken",
        "data": {
            "refreshToken": token
        }
    }
    rlt = sendRequest(data)
    code = rlt["code"]
    if int(code) != 0:
        return
    accessToken = rlt["result"]["accessToken"]
    refreshToken = rlt["result"]["refreshToken"]
    if accessToken is None or refreshToken is None:
        return
    setToken(accessToken, refreshToken)


def setToken(accessToken, refreshToken):
    data = {
        "accessToken": accessToken,
        "refreshToken": refreshToken
    }
    tokenData = json.dumps(data)
    fp = open(TOKEN_FILE_PATH, "w+")
    fp.write(tokenData)
    fp.close()


def getAccessToken():
    token = None
    try:
        fp = open(TOKEN_FILE_PATH, "r")
        jsonData = fp.read()
        data = json.loads(jsonData)
        token = data["accessToken"]
    except:
        pass
    return token


def getRefreshToken():
    token = None
    try:
        fp = open(TOKEN_FILE_PATH, "r")
        jsonData = fp.read()
        data = json.loads(jsonData)
        token = data["refreshToken"]
    except:
        pass
    return token





class IRDevice:


    @property
    def state(self):
        return self.acState

    @property
    def mode(self):
        return self.acMode

    @property
    def Speed(self):
        return self.acSpeed

    @property
    def tmp(self):
        return self.acTemp
    
    @property
    def targetTmp(self):
        return self.ttmp

    @property
    def is_on(self):
        return self.acState == 0

    def __init__(self, did):
        self.acState = AC_POWER_OFF
        self.acTemp = 0
        self.acMode = 0
        self.acDirect = 0
        self.acSpeed = 0
        self.ttmp = 0
        self.did = did
        self._getIrInfo()
        self.getAcState()

    def getAcState(self):
        data = {
            "intent": "query.ir.acState",
            "data": {
                "did": self.did
            }
        }
        rlt = sendRequest(data)
        state = rlt["result"]["acState"]
        self._formatAcState(state)

    def open(self):
        self._sendCommand("PO")

    def close(self):
        self._sendCommand("P1")

    def setTmp(self,tmps):
        tmp = int(tmps)
        self.ttmp = tmp
        cmd = "T" + str(tmp)
        self._sendCommand(cmd)

    def _getIrInfo(self):
        data = {
            "intent": "query.ir.info",
            "data": {
                "did": self.did
            }
        }
        rlt = sendRequest(data)
        self.brandId = rlt["result"]["brandId"]

    def _sendCommand(self, cmd):
        data = {
            "intent": "write.ir.click",
            "data": {
                "did": self.did,
                "brandId": self.brandId,
                "isAcMatch": 0,
                "acKey": cmd
            }
        }
        rlt = sendRequest(data)
        print(rlt)
        code = rlt["code"]
        if int(code) != 0:
            print(rlt)
            # 出现错误
            return
        state = rlt["result"]["acState"]
        self._formatAcState(state)        

    def _formatAcState(self, state):
        if state is None:
            return
        list = state.split("_")
        for i in list:
            if i.startswith("P"):
                self.acState = int(i[1:])
            elif i.startswith("M"):
                self.acMode = int(i[1:])
            elif i.startswith("S"):
                self.acSpeed = int(i[1:])
            elif i.startswith("D"):
                self.acDirect = int(i[1:])
            elif i.startswith("T"):
                self.acTemp = int(i[1:])
                self.ttmp = self.acTemp
        print(self.acTemp)



class AqaraClimate(ClimateEntity):

    def __init__(self, did):
        """Set up the Aqara climate devices."""
        device = IRDevice(did)
        self.device = device

    async def async_added_to_hass(self):
        """Register callbacks."""
        _LOGGER.debug("async_added_to_hass")

    def _after_update(self, climate):
        """Handle state update."""
        _LOGGER.debug("async update ha state")


    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_TARGET_TEMPERATURE

    @property
    def temperature_unit(self):
        """Return the unit of measurement used by the platform."""
        return TEMP_CELSIUS

    @property
    def hvac_mode(self):
        """Return current operation ie. heat, cool, idle."""
        if self.device.acState == AC_POWER_ON:
            return MODE_TO_STATE[self.device.mode]
        return HVAC_MODE_OFF

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        return SUPPORT_HVAC

    @property
    def current_temperature(self):
        """Return the current temperature."""
        t = int(self.device.tmp)
        return t

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        t = int(self.device.targetTmp)
        return t

    @property
    def is_on(self):
        """Return true if on."""
        return self.device.is_on

    # @property
    # def fan_mode(self):
    #     """Return the fan setting."""
    #     return self._current_fan_mode
    #
    # @property
    # def fan_modes(self):
    #     """Return the list of available fan modes."""
    #     return self._device.fan_list

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return 16

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return 32
    
    def turn_on(self):
        """Turn on ac."""
        self.device._sendCommand("P0")

    def turn_off(self):
        """Turn off ac."""
        self.device._sendCommand("P1")

    @property
    def unique_id(self):
        """Return the unique ID of the HVAC."""
        return f"{self.device.did}"


    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            self.device.setTmp(temperature)

        if (operation_mode := kwargs.get(ATTR_HVAC_MODE)) is not None:
            self.set_hvac_mode(operation_mode)

    def set_hvac_mode(self, hvac_mode):
        """Set new target operation mode."""
        if hvac_mode == HVAC_MODE_OFF:
            if self.is_on:
                self.turn_off()
            return
        if not self.is_on:
            self.turn_on()
        mode = STATE_TO_MODE[hvac_mode]
        cmd = "M"+str(mode)
        self.device._sendCommand(cmd)

    def set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        self.device._sendCommend("P3")
