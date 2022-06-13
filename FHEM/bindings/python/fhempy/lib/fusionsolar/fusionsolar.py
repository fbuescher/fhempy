import asyncio
import time

from fhempy.lib.fusionsolar.fusionsolar_api import FusionSolarRestApi

from .. import fhem, generic


class fusionsolar(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self._stationname = None
        self._sessionid = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        await super().Define(hash, args, argsh)
        if len(argsh) > 0 and argsh[list(argsh)[0]][:4] == "http":
            await fhem.readingsSingleUpdate(
                hash, "state", "Please read HELP to change define", 1
            )
            return

        if not (len(args) == 4 or len(args) == 5):
            return (
                "Usage: define my_solar fhempy fusionsolar "
                "[SESSIONID] [STATIONNAME] [REGION]"
            )

        self._sessionid = args[3]
        self._stationname = list(argsh)[0] + "=" + argsh[list(argsh)[0]]
        self._region = args[4] if len(args) == 5 else "region01eu5"

        await fhem.readingsSingleUpdate(hash, "state", "connecting", 1)
        self.create_async_task(self.update())

    async def update(self):
        self.restapi = FusionSolarRestApi(
            self.logger,
            self._sessionid,
            self._stationname,
            self._region,
        )

        await self.update_readings()

    async def update_readings(self):
        while True:
            await fhem.readingsBeginUpdate(self.hash)
            try:
                await self.restapi.update()

                await fhem.readingsBulkUpdate(
                    self.hash, "from_grid_power", self.restapi.from_grid_power
                )
                await fhem.readingsBulkUpdate(
                    self.hash, "to_grid_power", self.restapi.to_grid_power
                )
                await fhem.readingsBulkUpdate(
                    self.hash, "electrical_load", self.restapi.electrical_load
                )
                await fhem.readingsBulkUpdate(
                    self.hash, "grid_power", self.restapi.grid_power
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "inverter_output_power",
                    self.restapi.inverter_output_power,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "string_output_power",
                    self.restapi.string_output_power,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "daily_self_use_ratio",
                    self.restapi.daily_self_use_ratio,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "station",
                    self.restapi.station,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "co2_saved",
                    self.restapi.co2_saved,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "daily_self_use_energy",
                    self.restapi.daily_self_use_energy,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "daily_self_use_solar_ratio",
                    self.restapi.daily_self_use_solar_ratio,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "daily_use_energy",
                    self.restapi.daily_use_energy,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "grid_connected_time",
                    self.restapi.grid_connected_time,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "installed_capacity",
                    self.restapi.installed_capacity,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "total_current_day_energy",
                    self.restapi.total_current_day_energy,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "total_current_month_energy",
                    self.restapi.total_current_month_energy,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "total_current_year_energy",
                    self.restapi.total_current_year_energy,
                )
                await fhem.readingsBulkUpdate(
                    self.hash,
                    "total_lifetime_energy",
                    self.restapi.total_lifetime_energy,
                )

                # battery values
                if self.restapi.battery_soc is not None:
                    await fhem.readingsBulkUpdate(
                        self.hash,
                        "battery_soc",
                        self.restapi.battery_soc,
                    )
                    await fhem.readingsBulkUpdate(
                        self.hash,
                        "battery_power",
                        self.restapi.battery_power,
                    )
                    await fhem.readingsBulkUpdate(
                        self.hash,
                        "battery_charge_capacity",
                        self.restapi.battery_charge_capacity,
                    )
                    await fhem.readingsBulkUpdate(
                        self.hash,
                        "battery_discharge_capacity",
                        self.restapi.battery_discharge_capacity,
                    )

                await fhem.readingsBulkUpdateIfChanged(self.hash, "state", "connected")
            except Exception:
                await fhem.readingsBulkUpdateIfChanged(self.hash, "state", "failed")
                self.logger.exception("Failed to update readings")
            await fhem.readingsEndUpdate(self.hash, 1)
            # calculate next full 5min+30s
            next_sec = (
                (4 - time.localtime().tm_min % 5) * 60
                + 60
                - time.localtime().tm_sec
                + 30
            )
            if next_sec > 180:
                next_sec = 180
            await asyncio.sleep(next_sec)
