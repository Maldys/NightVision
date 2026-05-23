#!/usr/bin/env python3
import time
from smbus import SMBus

print("Start")
class ADS1115Reader:
    """
    ADS1115 I2C reader for Raspberry Pi (bus 1: GPIO2 SDA, GPIO3 SCL)

    - init() / end() for explicit lifetime control
    - supports context manager: with ADS1115Reader(...) as adc:
    - get_voltage(channel) returns input voltage (AINx vs GND) in volts
    - get_battery_voltage(channel) returns scaled voltage (e.g. for divider 1:1 -> *2)
    """

    REG_CONVERSION = 0x00
    REG_CONFIG = 0x01

    # MUX codes for single-ended:
    _MUX_SINGLE_ENDED = {
        0: 0b100,  # AIN0 vs GND
        1: 0b101,  # AIN1 vs GND
        2: 0b110,  # AIN2 vs GND
        3: 0b111,  # AIN3 vs GND
    }

    # Data rate bits (DR)
    _DR_BITS = {
        8: 0b000,
        16: 0b001,
        32: 0b010,
        64: 0b011,
        128: 0b100,
        250: 0b101,
        475: 0b110,
        860: 0b111,
    }

    # PGA full-scale volts (FS) and config bits
    _PGA = {
        6.144: 0b000,
        4.096: 0b001,
        2.048: 0b010,
        1.024: 0b011,
        0.512: 0b100,
        0.256: 0b101,  # same for 0b110, 0b111
    }

    def __init__(
        self,
        addr: int = 0x48,
        bus: int = 1,
        fs_volts: float = 4.096,
        data_rate_sps: int = 128,
        conversion_delay_s: float | None = None,
    ):
        """
        addr: ADS1115 I2C address (default 0x48)
        bus: I2C bus number on Raspberry Pi (default 1)
        fs_volts: full-scale range; choose from 6.144, 4.096, 2.048, 1.024, 0.512, 0.256
        data_rate_sps: one of 8,16,32,64,128,250,475,860
        conversion_delay_s: if None, auto choose safe delay from data rate
        """
        if fs_volts not in self._PGA:
            raise ValueError(f"fs_volts must be one of {sorted(self._PGA.keys())}")
        if data_rate_sps not in self._DR_BITS:
            raise ValueError(f"data_rate_sps must be one of {sorted(self._DR_BITS.keys())}")

        self.addr = addr
        self.bus_num = bus
        self.fs_volts = fs_volts
        self.data_rate_sps = data_rate_sps

        # Safe delay: slightly above one conversion period
        if conversion_delay_s is None:
            period = 1.0 / float(data_rate_sps)
            self.conversion_delay_s = max(0.001, period * 1.5)
        else:
            self.conversion_delay_s = conversion_delay_s

        self._bus: SMBus | None = None

    # ---------- lifecycle ----------
    def init(self) -> None:
        """Open I2C bus. Safe to call multiple times."""
        if self._bus is None:
            self._bus = SMBus(self.bus_num)

    def end(self) -> None:
        """Close I2C bus (disable). Safe to call multiple times."""
        if self._bus is not None:
            try:
                self._bus.close()
            finally:
                self._bus = None

    close = end  # alias

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.end()
        return False

    # ---------- core reading ----------
    @staticmethod
    def _to_int16(msb: int, lsb: int) -> int:
        val = (msb << 8) | lsb
        return val - 0x10000 if (val & 0x8000) else val

    def _write_config_single_shot(self, mux_bits: int) -> None:
        """
        Build config register for single-shot conversion:
        - OS=1 start conversion
        - MUX = channel
        - PGA = fs range
        - MODE=1 single-shot
        - DR = selected
        - comparator disabled
        """
        if self._bus is None:
            raise RuntimeError("ADS1115Reader not initialized. Call init() first.")

        pga_bits = self._PGA[self.fs_volts]
        dr_bits = self._DR_BITS[self.data_rate_sps]

        config = 0
        config |= (1 << 15)               # OS: start single conversion
        config |= ((mux_bits & 0x7) << 12)
        config |= (pga_bits << 9)
        config |= (1 << 8)                # MODE: single-shot
        config |= (dr_bits << 5)
        config |= 0b11                    # COMP_QUE: disable comparator

        msb = (config >> 8) & 0xFF
        lsb = config & 0xFF
        self._bus.write_i2c_block_data(self.addr, self.REG_CONFIG, [msb, lsb])

    def _read_conversion_raw(self) -> int:
        if self._bus is None:
            raise RuntimeError("ADS1115Reader not initialized. Call init() first.")

        data = self._bus.read_i2c_block_data(self.addr, self.REG_CONVERSION, 2)
        return self._to_int16(data[0], data[1])

    def get_voltage(self, channel: int) -> float:
        """
        Read single-ended channel 0/1 and return input voltage (AINx vs GND) in volts.
        """
        if channel not in self._MUX_SINGLE_ENDED:
            raise ValueError("channel must be 0..3")

        mux_bits = self._MUX_SINGLE_ENDED[channel]
        self._write_config_single_shot(mux_bits)

        # wait for conversion
        time.sleep(self.conversion_delay_s)

        raw = self._read_conversion_raw()

        volts = raw * (self.fs_volts / 32768.0)
        return volts

    

    def get_battery_voltage(self, channel: int) -> float:
        return round(self.get_voltage(channel) * 2, 2)+0.1
    
    def get_battery_percent(self, channel: int) -> float:
        return round((self.get_battery_voltage(channel)-3.66) / 0.0115, 2)

    def get_full_percent(self):
        val = self.get_battery_percent(0) + self.get_battery_percent(1)
        val = val/2.0

        return round(val,2)

        

