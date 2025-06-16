from pymavlink import mavutil
import json
from typing import Dict, List, Any
import io

class MavlinkParser:
    def __init__(self):
        self.message_types = {
            'CMD': [],
            'MSG': [],
            'FILE': [],
            'MODE': [],
            'AHR2': [],
            'ATT': [],
            'GPS': [],
            'POS': [],
            'XKQ1': [],
            'XKQ': [],
            'NKQ1': [],
            'NKQ2': [],
            'XKQ2': [],
            'PARM': [],
            'STAT': [],
            'EV': [],
            'XKF4': [],
            'FNCE': []
        }

    def parse_log(self, file_contents: bytes) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parse a MAVLink log file and return structured data
        """
        # Create a file-like object from the bytes
        file_obj = io.BytesIO(file_contents)
        
        # Create a MAVLink connection
        mlog = mavutil.mavlink_connection(file_obj)
        
        # Reset message storage
        for key in self.message_types:
            self.message_types[key] = []
        
        # Process all messages
        while True:
            try:
                msg = mlog.recv_match()
                if msg is None:
                    break
                    
                # Convert message to dictionary
                msg_dict = msg.to_dict()
                
                # Add timestamp
                msg_dict['timestamp'] = msg._timestamp
                
                # Store message based on its type
                msg_type = msg.get_type()
                if msg_type in self.message_types:
                    self.message_types[msg_type].append(msg_dict)
                    
            except Exception as e:
                print(f"Error processing message: {e}")
                continue
        
        return self.message_types

    def get_message_type(self, msg_type: str) -> List[Dict[str, Any]]:
        """
        Get all messages of a specific type
        """
        return self.message_types.get(msg_type, [])

    def trim_messages(self, start_time: float) -> None:
        """
        Remove messages before the specified timestamp
        """
        for msg_type in self.message_types:
            self.message_types[msg_type] = [
                msg for msg in self.message_types[msg_type]
                if msg['timestamp'] >= start_time
            ] 