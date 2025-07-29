<<<<<<< Updated upstream
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict


@dataclass
class CPUInfo:
=======
"""Data models for Linux system diagnostics collector."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class CPUInfo(BaseModel):
    """CPU information model."""
>>>>>>> Stashed changes
    model: str = "Unknown"
    architecture: str = "Unknown"
    cores: int = 0
    sockets: int = 0
    threads_per_core: int = 0
    max_frequency: str = "Unknown"
<<<<<<< Updated upstream
    temperatures: List[float] = field(default_factory=list)
    raw_lscpu: str = ""


@dataclass
class MemoryInfo:
=======
    temperatures: List[float] = []
    raw_lscpu: str = ""


class MemoryInfo(BaseModel):
    """Memory information model."""
>>>>>>> Stashed changes
    total: str = "Unknown"
    available: str = "Unknown"
    swap_total: str = "Unknown"
    swap_used: str = "Unknown"
    swapon_output: Optional[str] = None


<<<<<<< Updated upstream
@dataclass
class DiskDevice:
=======
class DiskDevice(BaseModel):
    """Disk device information model."""
>>>>>>> Stashed changes
    name: str
    size: str
    type: str
    mountpoint: Optional[str] = None


<<<<<<< Updated upstream
@dataclass
class NetworkInterface:
    name: str
    state: str
    ipv4: str
    speed: str


@dataclass
class HardwareInfo:
=======
class NetworkInterface(BaseModel):
    """Network interface information model."""
    name: str
    state: str
    ipv4: str
    speed: str = "unknown"


class HardwareInfo(BaseModel):
    """Complete hardware information model."""
>>>>>>> Stashed changes
    timestamp: datetime
    cpu: CPUInfo
    memory: MemoryInfo
    disks: List[DiskDevice]
    raw_smart: str = ""


<<<<<<< Updated upstream
@dataclass
class SystemReport:
    hardware: HardwareInfo
    processes: List[Dict]
    network: List[NetworkInterface]
    kernel: Dict
    collection_errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)
=======
class SystemReport(BaseModel):
    """Complete system diagnostics report model."""
    hardware: HardwareInfo
    processes: List[Dict[str, Any]] = []
    network: List[NetworkInterface]
    kernel: Dict[str, Any] = {}
    collection_errors: List[str] = []
>>>>>>> Stashed changes
