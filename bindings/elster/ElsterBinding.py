# -*- coding: utf-8 -*-
import time

import can
from can import Message
from typing import Dict, List
from typing import Set

import config
from bindings.BaseBinding import BaseBinding
from bindings.elster.Converter import DEC, CENT, OPERATING_MODE, ONE
from bindings.elster.ElsterFrame import ElsterFrame
from bindings.elster.Entry import SimpleEntry, BaseEntry, ReadOnlyFormulaEntry


class ElsterBinding(BaseBinding):
    # Only use one of this sender ids
    # 680 - PC (ComfortSoft)
    # 700 - Fremdgerät
    # 780 - DCF-Modul
    SENDER = 0x680

    #  Structure taken from "BEDIENUNG UND INSTALLATION Wärmepumpen-Manager WPM 3" Chapter 5
    #  https://www.stiebel-eltron.de/toolbox/datengrab/montageanweisung/de/DM0000031125.pdf
    ENTRIES = {
        # Boiler
        0x180: [
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # INFO / ANLAGE / HEIZUNG
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # AUSSENTEMPERATUR
            SimpleEntry('outside/environment/temperature', '°C', 0x000c, DEC),
            # ISTTEMPERATUR HK 1 - Heizkreis-Isttemperatur Heizkreis 1
            SimpleEntry('heating_circuit1/heating/temperature', '°C', 0x02ca, DEC),
            # SOLLTEMPERATUR HK 1 - Heizkreis-Solltemperatur Heizkreis 1 (HK1) bei Festwertregelung wird Festwerttemperatur angezeigt.
            SimpleEntry('heating_circuit1/heating/set_temperature', '°C', 0x01d7, DEC),

            # TODO
            # ISTTEMPERATUR HK 2 - Heizkreis-Isttemperatur Heizkreis 2
            # SOLLTEMPERATUR HK 2 - Heizkreis-Solltemperatur Heizkreis 2 (HK2) bei Festwertregelung wird Festwerttemperatur angezeigt.

            # VORLAUFISTTEMPERATUR WP - Wärmepumpen-Vorlauf-Isttemperatur
	    #SimpleEntry('heatpump/heating/flow_temperature', '°C', 0x000f, DEC),

            # VORLAUFISTTEMPERATUR NHZ - Nachheizstufen-Vorlauf-Isttemperatur
            SimpleEntry('booster/flow_temperature', '°C', 0x06a0, DEC),

            # RÜCKLAUFISTTEMPERATUR WP
            SimpleEntry('heatpump/heating/return_temperature', '°C', 0x0016, DEC),

            # TODO
            # FESTWERTSOLLTEMPERATUR

            # PUFFERISTTEMPERATUR - Pufferspeicher-Isttemperatur
            SimpleEntry('buffer/heating/temperature', '°C', 0x0078, DEC),
            # PUFFERSOLLTEMPERATUR - Pufferspeicher-Solltemperatur
            SimpleEntry('buffer/heating/set_temperature', '°C', 0x01d5, DEC),
            # HEIZUNGSDRUCK
            SimpleEntry('heating/pressure', 'bar', 0x0674, CENT),
            # VOLUMENSTROM
            SimpleEntry('system/hotwater/volumetric_flow_rate', 'l/min', 0x0673, CENT),
            # ANLAGENFROST
            SimpleEntry('system/freeze_temperature', '°C', 0x0a00, DEC),

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # INFO / ANLAGE / WARMWASSER
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # ISTTEMPERATUR - Warmwasser-Isttemperatur
            SimpleEntry('boiler/hotwater/temperature', '°C', 0x000e, DEC),
            # SOLLTEMPERATUR - Warmwasser-Solltemperatur
            SimpleEntry('boiler/hotwater/set_temperature', '°C', 0x0003, DEC),
            # VOLUMENSTROM -  same as INFO / ANLAGE / HEIZUNG / VOLUMENSTROM
            # SimpleEntry('heating/volumetric_flow_rate', 'l/min', 0x0673, CENT),

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # INFO / ANLAGE / ELEKTRISCHE NACHERWÄRMUNG
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # BIVALENZTEMPERATUR HZG - Bivalenzpunkt Heizung
            SimpleEntry('heatpump/heating/bivalence_temperatur', '°C', 0x01ac, DEC),
            # EINSATZGRENZE HZG - Einsatzgrenze Heizung
            SimpleEntry('heatpump/heating/limit_of_use_temperatur', '°C', 0x01ae, DEC),
            # BIVALENZTEMPERATUR WW - Bivalenzpunkt Warmwasser
            SimpleEntry('heatpump/hotwater/bivalence_temperatur', '°C', 0x01ad, DEC),
            # EINSATZGRENZE WW - Einsatzgrenze Warmwasser
            SimpleEntry('heatpump/hotwater/limit_of_use_temperatur', '°C', 0x01af, DEC),

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            #  Not yet matched
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            SimpleEntry('boiler/hotwater/set_temperature/comfort', '°C', 0x0013, DEC, True),
            SimpleEntry('boiler/hotwater/set_temperature/standby', '°C', 0x0a06, DEC, True),
            SimpleEntry('operating_mode', '', 0x0112, OPERATING_MODE, True),
        ],
        # heating unit
        0x500: [
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # INFO / ANLAGE / PROZESSDATEN
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # RÜCKLAUFTEMPERATUR °C
            SimpleEntry('inverter/return_temperature', '°C', 0x0016, DEC),
            # VORLAUFTEMPERATUR °C
            SimpleEntry('inverter/flow_temperature', '°C', 0x01d6, DEC),
            # FROSTSCHUTZTEMPERATUR °C
            SimpleEntry('inverter/freeze_protection_temperature', '°C', 0x0014, DEC),
            # AUSSENTEMPERATUR °C
            SimpleEntry('inverter/environment/temperature', '°C', 0x000c, DEC),

            # TODO
            # FORTLUFTTEMPERATUR °C

            # VERDAMPFERTEMPERATUR °C
            SimpleEntry('inverter/evaporator_temperature', '°C', 0x07a9, DEC),
            # REKUPERATORTEMPERATUR (Wärmetauscher) °C
            SimpleEntry('inverter/recuperator_temperature', '°C', 0x07a3, DEC),

            # TODO
            # SAUGGASTEMP VERDICHTER °C
            # SAUGGASTEMP ND VERDICHTER °C
            # SAUGGASTEMP HD VERDICHTER °C
            # ZWISCHENEINSPRITZUNGSTEMP °C

            # HEISSGASTEMPERATUR °C
            SimpleEntry('inverter/hot_gas_temperature', '°C', 0x0265, DEC),

            # TODO
            # VERFLÜSSIGERTEMPERATUR °C
            # ÖLSUMPFTEMPERATUR °C

            # DRUCK NIEDERDRUCK bar
            SimpleEntry('inverter/low_pressure', 'bar', 0x07a7, CENT),

            # TODO
            # DRUCK MITTELDRUCK bar
            # DRUCK HOCHDRUCK bar
            SimpleEntry('inverter/high_pressure', 'bar', 0x07a6, CENT),

            # TODO
            # SPANNUNGSEINGANG DIFF DRUCK V
            # DIFFERENZ DRUCK mbar
            # WP WASSERVOLUMENSTROM l/min
            # STROM INVERTER ND A
            # STROM INVERTER HD A
            # STROM INVERTER A
            # SPANNUNG INVERTER V
            # DREHZAHL ND Hz
            # SOLLDREHZAHL ND Hz
            # DREHZAHL HD Hz
            # SOLLDREHZAHL HD Hz
            # ISTDREHZAHL VERDICHTER Hz
            # SOLLDREHZAHL VERDICHTER Hz
            # LÜFTERLEISTUNG REL %
            # ISTDREHZAHL LUEFTER Hz
            # SOLLDREHZAHL LUEFTER Hz
            # VERDAMPFEREINGANGSTEMPERATUR °C

        ],
        # Verdichter ???
        0x514: [
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # INFO / ANLAGE / WÄRMEMENGE
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # VD HEIZEN TAG - Wärmemenge des Verdichters im Heizbetrieb seit 0:00 Uhr des aktuellen Tages.
            ReadOnlyFormulaEntry('compressor/heating/heat_output/day', 'Wh', 'A * 1000 + B', {'A': 0x092f, 'B': 0x092e}),
            # VD HEIZEN SUMME - Gesamtsumme der Wärmemenge des Verdichters im Heizbetrieb.
            ReadOnlyFormulaEntry('compressor/heating/heat_output', 'Wh', 'A * 1000000 + (B+C) * 1000 + D', {'A': 0x0931, 'B': 0x0930, 'C': 0x092f, 'D': 0x092e}),
            # VD WARMWASSER TAG - Wärmemenge des Verdichters im Warmwasserbetrieb seit 0:00 Uhr des aktuellen Tages.
            ReadOnlyFormulaEntry('compressor/hotwater/heat_output/day', 'Wh', 'A * 1000 + B', {'A': 0x092b, 'B': 0x092a}),
            # VD WARMWASSER SUMME - Gesamtsumme der Wärmemenge des Verdichters im Warmwasserbetrieb.
            ReadOnlyFormulaEntry('compressor/hotwater/heat_output', 'Wh', 'A * 1000000 + (B+C) * 1000 + D', {'A': 0x092d, 'B': 0x092c, 'C': 0x092b, 'D': 0x092a}),

            # NHZ HEIZEN SUMME - Gesamtsumme der Wärmemenge der Nachheizstufen im Heizbetrieb.
            ReadOnlyFormulaEntry('booster/heating/heat_output', 'Wh', 'A * 1000000 + B * 1000 + C', {'A': 0x0929, 'B': 0x0927, 'C': 0x0926}),
            # NHZ WARMWASSER SUMME - Gesamtsumme der Wärmemenge der Nachheizstufen im Warmwasserbetrieb.
            ReadOnlyFormulaEntry('booster/hotwater/heat_output', 'Wh', 'A * 1000000 + B * 1000 + C', {'A': 0x0925, 'B': 0x0923, 'C': 0x0922}),

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # INFO / ANLAGE / LEISTUNGSAUFNAHME
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # VD HEIZEN TAG - Elektrische Leistung des Verdichters im Heizbetrieb seit 0:00 Uhr des aktuellen Tages.
            ReadOnlyFormulaEntry('compressor/heating/energy_input/day', 'Wh', 'A * 1000 + B', {'A': 0x091f, 'B': 0x091e}),
            # VD HEIZEN SUMME - Gesamtsumme der Elektrischen Leistung des Verdichters im Heizbetrieb.
            ReadOnlyFormulaEntry('compressor/heating/energy_input', 'Wh', 'A * 1000000 + (B+C) * 1000 + D', {'A': 0x0921, 'B': 0x0920, 'C': 0x091f, 'D': 0x091e}),
            # VD WARMWASSER TAG - Elektrische Leistung des Verdichters im Warmwasserbetrieb seit 0:00 Uhr des aktuellen Tages.
            ReadOnlyFormulaEntry('compressor/hotwater/energy_input/day', 'Wh', 'A * 1000 + B', {'A': 0x091b, 'B': 0x091a}),
            # VD WARMWASSER SUMME - Gesamtsumme der Elektrischen Leistung des Verdichters im Warmwasserbetrieb.
            ReadOnlyFormulaEntry('compressor/hotwater/energy_input', 'Wh', 'A * 1000000 + (B+C) * 1000 + D', {'A': 0x091d, 'B': 0x091c, 'C': 0x091b, 'D': 0x091a}),

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # INFO / ANLAGE / LAUFZEITEN
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # VD HEIZEN - Laufzeit des Verdichters im Heizbetrieb. Stunden
            SimpleEntry('compressor/heating/operating_hours', 'h', 0x07fc, ONE),

            # TODO
            # VD 1 HEIZEN - Laufzeit des Verdichters 1 im Heizbetrieb. Stunden
            # VD 2 HEIZEN - Laufzeit des Verdichters 2 im Heizbetrieb. Stunden
            # VD 1/2 HEIZEN - Laufzeit des Verdichters 1 und 2 im Heizbetrieb. Stunden

            # VD WARMWASSER - Laufzeit des Verdichters im Warmwasserbetrieb. Stunden
            SimpleEntry('compressor/hotwater/operating_hours', 'h', 0x0802, ONE),

            # TODO
            # VD 1 WARMWASSER - Laufzeit des Verdichters 1 im Warmwasserbetrieb. Stunden
            # VD 2 WARMWASSER - Laufzeit des Verdichters 2 im Warmwasserbetrieb. Stunden
            # VD 1/2 WARMWASSER - Laufzeit des Verdichters 1 und 2 im Warmwasserbetrieb. Stunden
            # VD KÜHLEN - Laufzeit des Verdichters im Kühlbetrieb. Stunden
            # VD ABTAUEN - Laufzeit des Verdichters im Abtaubetrieb. Stunden
            SimpleEntry('compressor/unfreeze/operating_hours', 'h', 0x0808, ONE),

            # TODO
            # VD 1 ABTAUEN - Laufzeit des Verdichters 1 im Abtaubetrieb.  Stunden
            # VD 2 ABTAUEN - Laufzeit des Verdichters 2 im Abtaubetrieb. Stunden

            # NHZ 1 - Laufzeit der elektrischen Not-/Zusatzheizung in der Nachheizstufe 1. Stunden
            SimpleEntry('booster/operating_hours/level1', 'h', 0x0259, ONE),
            # NHZ 2 - Laufzeit der elektrischen Not-/Zusatzheizung in der Nachheizstufe 2. Stunden
            SimpleEntry('booster/operating_hours/level2', 'h', 0x025a, ONE),
            # NHZ 1 / 2 -  Laufzeit der elektrischen Not-/Zusatzheizung in den Nachheizstufen 1 und 2. Stunden
            SimpleEntry('booster/operating_hours', 'h', 0x0805, ONE),
            # ZEIT ABTAUEN Minuten
            SimpleEntry('compressor/unfreeze/operating_minutes', 'min', 0x0807, ONE),
            # STARTS ABTAUEN
            SimpleEntry('compressor/unfreeze/starts', '', 0x0806, ONE),

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # INFO / ANLAGE / STARTS
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # VERDICHTER
            ReadOnlyFormulaEntry('compressor/starts', '', 'A * 1000 + B', {'A': 0x071c, 'B': 0x071d}),
            # TODO
            # VERDICHTER 1
            # VERDICHTER 2
        ]
    }  # type: Dict[int, List[BaseEntry]]

    def __init__(self, heat_pump_id):
        topics = []
        self.base_topic = 'heatpump/' + heat_pump_id + '/'
        self.ids_per_receiver = {}  # type: Dict[int, Set[int]]

        for receiver, entries in list(self.ENTRIES.items()):
            elster_ids = set()  # type: Set[int]
            self.ids_per_receiver[receiver] = elster_ids
            for entry in entries:
                elster_ids.update(entry.getElsterIndices())
                topic = entry.getTopicForUpdates()
                if topic is not None:
                    topics.append(self.base_topic + topic)

        super(ElsterBinding, self).__init__(heat_pump_id, topics)

        # noinspection PyTypeChecker
        self.bus = can.Bus(bustype='socketcan_native', channel='can0', receive_own_messages=False)
        can.Notifier(self.bus, [self.onCanMessage])

    def onApiMessage(self, topic, payload):
        # type: (str, object) -> None
        print("API message ", topic, ": ", payload)
        if not str.startswith(topic, self.base_topic):
            return
        topic = str.replace(topic, self.base_topic, '')

        for receiver, entries in list(self.ENTRIES.items()):
            for entry in entries:  # type: BaseEntry
                if entry.isUpdatableByTopic(topic):
                    can_value = entry.convertApiValueToCan(payload)
                    if isinstance(can_value, int):
                        frame = ElsterFrame(sender=ElsterBinding.SENDER, receiver=receiver, elster_index=entry.getElsterIndices()[0],
                                            message_type=ElsterFrame.WRITE, value=can_value)
                        print(frame)
                        self.bus.send(frame.getCanMessage())

    def onCanMessage(self, msg):
        # type: (Message) -> None
        frame = ElsterFrame(msg=msg)
        if config.BINDING['handle_all_messages'] is False and frame.receiver != ElsterBinding.SENDER:
            # only parse messages directly send to us
            return
        if msg.arbitration_id not in self.ENTRIES:
            return
        for entry in self.ENTRIES[msg.arbitration_id]:
            can_value = entry.parseCanValue(frame.elster_index, frame.value)
            if can_value is not None:
                topic = self.base_topic + entry.publishing_topic
                print(topic, can_value, entry.unit)
                for bridge in self.bridges:
                    try:
                        bridge.publishApiMessage(self.heat_pump_id, self.base_topic, entry.publishing_topic, can_value)
                    except BaseException as err:
                        print(f"Unexpected {err=}, {type(err)=}")

    def resetValues(self):
        for entries in list(self.ENTRIES.values()):  # type: List[BaseEntry]
            for entry in entries:
                entry.resetValues()

    def queryForData(self):
        self.resetValues()

        for (receiver, entries) in list(self.ids_per_receiver.items()):
            for entry in entries:
                # send a read request, the corresponding device will answer with the value
                frame = ElsterFrame(sender=ElsterBinding.SENDER, receiver=receiver, elster_index=entry, message_type=ElsterFrame.READ)
                self.bus.send(frame.getCanMessage())
                time.sleep(0.01)
