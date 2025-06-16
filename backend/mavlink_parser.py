from pymavlink import mavutil
import json
from typing import Dict, List, Any
import io
import logging
import traceback

logger = logging.getLogger(__name__)

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
            'FNCE': [],
            'BAT': [],  # Added battery messages
            'RCIN': [],  # Added RC input messages
            'RCOU': [],  # Added RC output messages
            'SYS': [],   # Added system status messages
            'POWR': [],  # Added power messages
            'CURR': [],  # Added current messages
            'VIBE': [],  # Added vibration messages
            'IMU': [],   # Added IMU messages
            'MAG': [],   # Added magnetometer messages
            'BARO': [],  # Added barometer messages
            'RATE': [],  # Added rate messages
            'VFR': [],   # Added VFR messages
            'TERR': [],  # Added terrain messages
            'WIND': [],  # Added wind messages
            'RPM': [],   # Added RPM messages
            'TEMP': [],  # Added temperature messages
            'DIST': [],  # Added distance messages
            'FENCE': [], # Added fence messages
            'MISSION': [] # Added mission messages
        }

    def parse_log(self, file_contents: bytes) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parse a MAVLink log file and return structured data
        """
        try:
            logger.debug("Creating file-like object from bytes")
            # Create a file-like object from the bytes
            file_obj = io.BytesIO(file_contents)
            
            logger.debug("Creating MAVLink connection")
            # Create a MAVLink connection
            try:
                mlog = mavutil.mavlink_connection(file_obj)
            except Exception as mavlink_error:
                logger.error(f"Error creating MAVLink connection: {str(mavlink_error)}")
                logger.error(traceback.format_exc())
                raise ValueError(f"Invalid MAVLink log file: {str(mavlink_error)}")
            
            # Reset message storage
            for key in self.message_types:
                self.message_types[key] = []
            
            message_count = 0
            error_count = 0
            unknown_types = set()
            
            logger.debug("Starting message processing")
            # Process all messages
            while True:
                try:
                    msg = mlog.recv_match()
                    if msg is None:
                        break
                        
                    # Convert message to dictionary
                    try:
                        msg_dict = msg.to_dict()
                    except Exception as dict_error:
                        logger.warning(f"Error converting message to dict: {str(dict_error)}")
                        error_count += 1
                        continue
                    
                    # Add timestamp
                    try:
                        msg_dict['timestamp'] = msg._timestamp
                    except AttributeError:
                        logger.warning("Message has no timestamp attribute")
                        msg_dict['timestamp'] = 0
                    
                    # Store message based on its type
                    msg_type = msg.get_type()
                    if msg_type in self.message_types:
                        self.message_types[msg_type].append(msg_dict)
                        message_count += 1
                    else:
                        unknown_types.add(msg_type)
                        logger.debug(f"Unknown message type: {msg_type}")
                        
                except Exception as e:
                    error_count += 1
                    logger.warning(f"Error processing message: {str(e)}")
                    continue
            
            logger.info(f"Successfully parsed {message_count} messages with {error_count} errors")
            if unknown_types:
                logger.info(f"Found unknown message types: {unknown_types}")
            
            # Validate the parsed data
            if message_count == 0:
                logger.error("No valid messages found in the log file")
                raise ValueError("No valid messages found in the log file")
            
            # Log message type statistics
            for msg_type, messages in self.message_types.items():
                if messages:
                    logger.info(f"Found {len(messages)} messages of type {msg_type}")
            
            return self.message_types
            
        except Exception as e:
            logger.error(f"Error parsing log file: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def get_message_type(self, msg_type: str) -> List[Dict[str, Any]]:
        """
        Get all messages of a specific type
        """
        if msg_type not in self.message_types:
            logger.warning(f"Requested unknown message type: {msg_type}")
            return []
        return self.message_types.get(msg_type, [])

    def trim_messages(self, start_time: float) -> None:
        """
        Remove messages before the specified timestamp
        """
        for msg_type in self.message_types:
            original_count = len(self.message_types[msg_type])
            self.message_types[msg_type] = [
                msg for msg in self.message_types[msg_type]
                if msg['timestamp'] >= start_time
            ]
            removed_count = original_count - len(self.message_types[msg_type])
            if removed_count > 0:
                logger.info(f"Removed {removed_count} messages from {msg_type} before timestamp {start_time}") 