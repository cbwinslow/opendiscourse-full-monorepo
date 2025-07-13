from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict


@dataclass
class CPUInfo:
    model: str = "Unknown"
    architecture: str = "Unknown"
    cores: int = 0
    sockets: int = 0
    threads_per_core: int = 0
    max_frequency: str = "Unknown"
    temperatures: List[float] = field(default_factory=list)
    raw_lscpu: str = ""


@dataclass
class MemoryInfo:
    total: str = "Unknown"
    available: str = "Unknown"
    swap_total: str = "Unknown"
    swap_used: str = "Unknown"
    swapon_output: Optional[str] = None


@dataclass
class DiskDevice:
    name: str
    size: str
    type: str
    mountpoint: Optional[str] = None


@dataclass
class NetworkInterface:
    name: str
    state: str
    ipv4: str
    speed: str


@dataclass
class HardwareInfo:
    timestamp: datetime
    cpu: CPUInfo
    memory: MemoryInfo
    disks: List[DiskDevice]
    raw_smart: str = ""


@dataclass
class SystemReport:
    hardware: HardwareInfo
    processes: List[Dict]
    network: List[NetworkInterface]
    kernel: Dict
    collection_errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)
