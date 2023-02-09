import queue
from .camera import Camera
from .config import EyeTrackConfig, CameraConfig, OSCConfig
from .logger import get_logger
from .tracker import Tracker
from .osc import VRChatOSCReceiver, VRChatOSC
from fastapi import APIRouter
from .types import EyeID, EyeData

logger = get_logger()


class ETVR:
    def __init__(self):
        self.config: EyeTrackConfig = EyeTrackConfig()
        self.config.load()
        # OSC stuff
        self.osc_queue: queue.Queue[EyeData] = queue.Queue()
        self.osc_sender: VRChatOSC = VRChatOSC(self.config, self.osc_queue)
        self.osc_receiver: VRChatOSCReceiver = VRChatOSCReceiver(self.config)
        # Trackers
        self.tracker_left: Tracker = Tracker(EyeID.LEFT, self.config, self.osc_queue)
        self.tracker_right: Tracker = Tracker(EyeID.RIGHT, self.config, self.osc_queue)
        # Object for fastapi routes
        self.router: APIRouter = APIRouter()

    def __del__(self):
        logger.debug("Deleting ETVR")
        self.stop()

    def add_routes(self) -> None:
        logger.debug("Adding routes to ETVR")
        self.router.add_api_route("/etvr/config", self.config.update, methods=["POST"])
        self.router.add_api_route("/etvr/config", self.config.return_config, methods=["GET"])
        self.router.add_api_route("/etvr/start", self.start, methods=["GET"])
        self.router.add_api_route("/etvr/stop", self.stop, methods=["GET"])
        self.router.add_api_route("/etvr/restart", self.restart, methods=["GET"])

    def start(self) -> None:
        logger.debug("Starting ETVR")
        self.tracker_left.start()
        self.tracker_right.start()
        logger.debug("ETVR started")

    def stop(self) -> None:
        logger.debug("Stopping ETVR")
        self.tracker_left.stop()
        self.tracker_right.stop()
        logger.debug("ETVR stopped")

    def restart(self) -> None:
        logger.debug("Restarting ETVR")
        self.stop()
        self.start()
        logger.debug("ETVR restarted")