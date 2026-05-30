from typing import Literal

class CongestionControl:
    def __init__(self, MSS: int):
        self.current_state: Literal["slow start", "congestion avoidance"] = "slow start"
        self.MSS: int = MSS
        self.cwnd: float = self.MSS
        self.ssthresh: float | None = None

    def get_cwnd(self) -> int:
        return int(self.cwnd)
    
    def get_MSS_in_cwnd(self) -> int:
        return self.get_cwnd() // self.MSS
    
    def event_ack_received(self):
        match self.current_state:
            case "slow start":
                self.cwnd += self.MSS
                if self.ssthresh != None and self.cwnd >= self.ssthresh:
                    self.current_state = "congestion avoidance"
            case "congestion avoidance":
                self.cwnd += self.MSS / self.get_MSS_in_cwnd()

    def event_timeout(self):
        match self.current_state:
            case "slow start":
                if self.ssthresh==None:
                    self.ssthresh = self.get_cwnd()/2
                    self.cwnd = self.MSS
            case "congestion avoidance":
                self.current_state = "slow start"
                self.ssthresh = self.get_cwnd()/2
                self.cwnd = self.MSS

    def is_state_slow_start(self):
        return self.current_state=="slow start"
    
    def is_state_congestion_avoidance(self):
        return self.current_state=="congestion avoidance"
    
    def get_ssthresh(self) -> int | None:
        return int(self.ssthresh) if self.ssthresh != None else self.ssthresh


