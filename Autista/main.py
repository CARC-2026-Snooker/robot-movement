from pathlib import Path
import sys

lib_dir = Path(__file__).resolve().parent.parent
if str(lib_dir) not in sys.path:
    sys.path.append(str(lib_dir))

from library import MotorBoard, ServoBoad, PrizmBoard