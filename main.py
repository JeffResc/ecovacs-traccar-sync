import aiohttp
import asyncio
import logging
import time
import asyncio
import logging
import os

from deebot_client.api_client import ApiClient as DeebotClient
from deebot_client.authentication import Authenticator, create_rest_config
from deebot_client.events import GpsPositionEvent, BatteryEvent, PositionsEvent
from deebot_client.mqtt_client import MqttClient, create_mqtt_config
from deebot_client.util import md5
from deebot_client.device import Device
from traccar_client import send_osmand_position

device_id = md5(str(time.time()))
account_id = os.getenv("ECOVACS_EMAIL")
password_hash = md5(os.getenv("EVOVACS_PASSWORD"))
country = os.getenv("COUNTRY_CODE")
traccar_url = os.getenv("TRACCAR_URL")

lastKnownBattery = None

async def sendGpsPositionToTraccar(bot: Device, event: GpsPositionEvent):
    global lastKnownBattery
    did = bot.device_info["did"]
    await send_osmand_position(traccar_url, did, event.latitude, event.longitude, battery=lastKnownBattery)

async def main():
  async with aiohttp.ClientSession() as session:
    logging.basicConfig(level=logging.DEBUG)
    rest_config = create_rest_config(session, device_id=device_id, alpha_2_country=country)

    authenticator = Authenticator(rest_config, account_id, password_hash)
    deebot_api_client = DeebotClient(authenticator)

    devices_ = await deebot_api_client.get_devices()

    bot = Device(devices_.mqtt[0], authenticator)

    mqtt_config = create_mqtt_config(device_id=device_id, country=country)
    mqtt = MqttClient(mqtt_config, authenticator)
    await bot.initialize(mqtt)

    async def on_gps_position(event: GpsPositionEvent):
      await sendGpsPositionToTraccar(bot, event)
    
    async def on_battery(event: BatteryEvent):
      global lastKnownBattery
      lastKnownBattery = event.value

    async def on_positions(event: PositionsEvent):
      print("POS", event)

    bot.events.subscribe(GpsPositionEvent, on_gps_position)
    bot.events.subscribe(BatteryEvent, on_battery)
    bot.events.subscribe(PositionsEvent, on_positions)

if __name__ == '__main__':
  loop = asyncio.get_event_loop()
  loop.create_task(main())
  loop.run_forever()
