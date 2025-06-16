import os
from typing import Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

class ChatAgent:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.sessions: Dict[str, List[Dict[str, str]]] = {}
        self.flight_data: Dict[str, Dict] = {}  # Store flight data per session

    def set_flight_data(self, session_id: str, flight_data: Dict) -> None:
        """Store flight data for a session"""
        self.flight_data[session_id] = flight_data

    def process_message(self, message: str, session_id: Optional[str] = None) -> str:
        """
        Process a user message and return a response
        """
        if session_id is None:
            session_id = "default"
            
        if session_id not in self.sessions:
            self.sessions[session_id] = []
            
        # Add user message to session history
        self.sessions[session_id].append({
            "role": "user",
            "content": message
        })

        # Get flight data for context if available
        flight_context = ""
        if session_id in self.flight_data:
            flight_data = self.flight_data[session_id]
            flight_context = self._prepare_flight_context(flight_data)
        
        try:
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are an expert UAV flight data analyst. 
                        Your role is to help users understand their flight logs and identify potential issues.
                        Be concise and technical in your responses.
                        
                        You have access to the following flight data:
                        {flight_context}
                        
                        You can analyze:
                        1. Flight parameters (altitude, speed, position)
                        2. System status (GPS, battery, RC signal)
                        3. Error messages and events
                        4. Flight modes and commands
                        
                        When analyzing data:
                        - Look for patterns and anomalies
                        - Consider the context of the flight
                        - Explain technical terms when needed
                        - Suggest potential solutions for issues
                        
                        Documentation reference: https://ardupilot.org/plane/docs/logmessages.html"""
                    },
                    *self.sessions[session_id]
                ]
            )
            
            # Extract the response text
            response_text = response.choices[0].message.content
            
            # Add assistant response to session history
            self.sessions[session_id].append({
                "role": "assistant",
                "content": response_text
            })
            
            return response_text
            
        except Exception as e:
            return f"Error processing message: {str(e)}"

    def _prepare_flight_context(self, flight_data: Dict) -> str:
        """Prepare flight data context for the LLM"""
        context = []
        
        # Add basic flight info
        if 'GPS' in flight_data:
            gps_data = flight_data['GPS']
            if gps_data:
                context.append(f"Flight duration: {gps_data[-1]['timestamp'] - gps_data[0]['timestamp']:.1f} seconds")
                context.append(f"GPS points: {len(gps_data)}")
        
        # Add altitude info
        if 'ATT' in flight_data:
            att_data = flight_data['ATT']
            if att_data:
                altitudes = [msg.get('alt', 0) for msg in att_data if 'alt' in msg]
                if altitudes:
                    context.append(f"Altitude range: {min(altitudes):.1f}m to {max(altitudes):.1f}m")
        
        # Add battery info
        if 'BAT' in flight_data:
            bat_data = flight_data['BAT']
            if bat_data:
                voltages = [msg.get('volt', 0) for msg in bat_data if 'volt' in msg]
                if voltages:
                    context.append(f"Battery voltage range: {min(voltages):.1f}V to {max(voltages):.1f}V")
        
        # Add error messages
        if 'EV' in flight_data:
            ev_data = flight_data['EV']
            if ev_data:
                context.append(f"Number of events: {len(ev_data)}")
        
        return "\n".join(context)

    def detect_anomalies(self, flight_data: Dict) -> List[Dict]:
        """
        Analyze flight data for anomalies
        """
        anomalies = []
        
        # Check for common anomalies
        if 'ATT' in flight_data:
            att_data = flight_data['ATT']
            for i in range(1, len(att_data)):
                # Check for sudden attitude changes
                roll_diff = abs(att_data[i].get('roll', 0) - att_data[i-1].get('roll', 0))
                pitch_diff = abs(att_data[i].get('pitch', 0) - att_data[i-1].get('pitch', 0))
                
                if roll_diff > 45 or pitch_diff > 45:
                    anomalies.append({
                        'type': 'sudden_attitude_change',
                        'timestamp': att_data[i].get('timestamp', 0),
                        'severity': 'high',
                        'description': f'Sudden attitude change detected: roll={roll_diff:.1f}°, pitch={pitch_diff:.1f}°'
                    })
        
        if 'GPS' in flight_data:
            gps_data = flight_data['GPS']
            for i in range(1, len(gps_data)):
                # Check for GPS signal loss
                if gps_data[i].get('fix_type', 0) < 3:
                    anomalies.append({
                        'type': 'gps_signal_loss',
                        'timestamp': gps_data[i].get('timestamp', 0),
                        'severity': 'medium',
                        'description': f'GPS signal degraded or lost (fix_type={gps_data[i].get("fix_type", 0)})'
                    })
        
        # Check for battery issues
        if 'BAT' in flight_data:
            bat_data = flight_data['BAT']
            for i in range(1, len(bat_data)):
                if bat_data[i].get('volt', 0) < 10.5:  # Assuming 3S LiPo
                    anomalies.append({
                        'type': 'low_battery',
                        'timestamp': bat_data[i].get('timestamp', 0),
                        'severity': 'high',
                        'description': f'Low battery voltage: {bat_data[i].get("volt", 0):.1f}V'
                    })
        
        # Check for RC signal issues
        if 'RCIN' in flight_data:
            rcin_data = flight_data['RCIN']
            for i in range(1, len(rcin_data)):
                if rcin_data[i].get('rssi', 0) < 50:  # Arbitrary threshold
                    anomalies.append({
                        'type': 'rc_signal_weak',
                        'timestamp': rcin_data[i].get('timestamp', 0),
                        'severity': 'medium',
                        'description': f'Weak RC signal: {rcin_data[i].get("rssi", 0)}%'
                    })
        
        return anomalies 