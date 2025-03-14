#! /bin/false --

from pathlib import Path
from string import digits
from typing import Dict, Iterator

from migen.fhdl.module import Module
from migen.fhdl.specials import Instance
from migen.fhdl.structure import Signal


class ZynqUltraPsE(Module):
    PINS_TXT = "pins.txt"
    PIN_X_TXT = "pins.{}.txt"
    ENCODING = "utf-8"

    def __init__(self, export_dir: Path):
        self.inputs: Dict[str, Signal] = {}
        self.outputs: Dict[str, Signal] = {}
        self._glue: Dict[str, Signal] = {}
        for pin_name in self._get_pin_names(export_dir / self.PINS_TXT):
            pin_props = self._read_properties(export_dir / self.PIN_X_TXT.format(pin_name))
            self._import_pin(pin_props)
        self._instance_zynq()

    @classmethod
    def _get_pin_names(cls, path: Path) -> Iterator[str]:
        with path.open(encoding=cls.ENCODING) as f:
            for pin_name in f:
                pin_name = pin_name.strip()
                if pin_name != "":
                    yield pin_name

    @classmethod
    def _read_properties(cls, path: Path) -> Dict[str, str]:
        props = {}
        with path.open(encoding=cls.ENCODING) as f:
            for line in f:
                words = list(map(str.strip, line.split(maxsplit=3)))
                assert len(words) in [3, 4]
                if words == ["Property", "Type", "Read-only", "Value"]:
                    continue
                assert words[1] in ["string"]
                assert words[2] in ["true", "false"]
                key = words[0]
                value = "".join(words[3:])
                props[key] = value
        return props

    def _import_pin(self, pin_props: Dict[str, str]) -> None:
        assert "NAME" in pin_props
        assert "DIR" in pin_props
        assert "TYPE" in pin_props
        assert "LEFT" in pin_props
        assert "RIGHT" in pin_props
        assert "DEFAULT_DRIVER" in pin_props

        pin_name = pin_props["NAME"]
        assert pin_name != ""
        pin_dir = pin_props["DIR"]
        pin_dir_to_collection = {"I": self.inputs, "O": self.outputs}
        assert pin_dir in pin_dir_to_collection
        collection = pin_dir_to_collection[pin_dir]
        assert pin_name not in collection

        pin_type = pin_props["TYPE"]
        pin_type_to_importer = {
            "undef": self._import_pin_undef,
            "intr": self._import_pin_intr,
            "clk": self._import_pin_clk,
            "rst": self._import_pin_rst,
        }
        assert pin_type in pin_type_to_importer
        importer = pin_type_to_importer[pin_type]
        collection[pin_name] = importer(pin_props)

    def _import_pin_undef(self, pin_props: Dict[str, str]) -> Signal:
        assert set(pin_props["LEFT"]).issubset(digits)
        assert set(pin_props["RIGHT"]).issubset(digits)
        assert set(pin_props["DEFAULT_DRIVER"]).issubset("01")

        pin_name = pin_props["NAME"]
        left = int(pin_props["LEFT"] or 0)
        right = int(pin_props["RIGHT"] or 0)
        width = left - right + 1
        assert width > 0

        default = pin_props["DEFAULT_DRIVER"]
        if default == "":
            signal = Signal(bits_sign=(left + 1, False), name=pin_name, reset_less=True)
        else:
            signal = Signal(bits_sign=(left + 1, False), name=pin_name, reset=int(default, 2))
        signal_shifted = Signal(bits_sign=(width, False), name=f"{pin_name}__SHIFTED", reset_less=True)
        self.comb += signal_shifted.eq(signal[right : left + 1])

        self._glue[pin_name] = signal

        return signal_shifted

    def _import_pin_intr(self, pin_props: Dict[str, str]) -> Signal:
        return self._import_pin_undef(pin_props)

    def _import_pin_clk(self, pin_props: Dict[str, str]) -> Signal:
        assert pin_props["LEFT"] == ""
        assert pin_props["RIGHT"] == ""
        assert pin_props["DEFAULT_DRIVER"] == ""

        return self._import_pin_undef(pin_props)

    def _import_pin_rst(self, pin_props: Dict[str, str]) -> Signal:
        assert pin_props["LEFT"] == ""
        assert pin_props["RIGHT"] == ""

        return self._import_pin_undef(pin_props)

    def _instance_zynq(self) -> None:
        pin_mapping = {}
        for pin_name in self.inputs:
            signal = self._glue[pin_name]
            pin_mapping[f"i_{pin_name}"] = signal
        for pin_name in self.outputs:
            signal = self._glue[pin_name]
            pin_mapping[f"o_{pin_name}"] = signal
        self.specials += Instance("platform_zynq_ultra_ps_e_0_0", **pin_mapping)
