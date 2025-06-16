<template>
  <div class="chat-container">
    <div class="chat-header">
      <h3>Flight Data Assistant</h3>
      <div v-if="hasFlightData" class="flight-info">
        <span class="info-item" v-if="flightDuration">
          Duration: {{ formatDuration(flightDuration) }}
        </span>
        <span class="info-item" v-if="altitudeRange">
          Altitude: {{ altitudeRange }}
        </span>
        <span class="info-item" v-if="batteryRange">
          Battery: {{ batteryRange }}
        </span>
      </div>
    </div>

    <div class="chat-messages" ref="messageContainer">
      <div v-for="(message, index) in messages" :key="index"
           :class="['message', message.role]">
        <div class="message-content">
          {{ message.content }}
        </div>
      </div>
    </div>

    <div class="chat-input">
      <input
        v-model="newMessage"
        @keyup.enter="sendMessage"
        placeholder="Ask about your flight data..."
        :disabled="isLoading || !hasFlightData"
      />
      <button @click="sendMessage" :disabled="isLoading || !hasFlightData">
        {{ isLoading ? 'Sending...' : 'Send' }}
      </button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
    name: 'ChatBot',
    props: {
        flightData: {
            type: Object,
            default: () => ({})
        }
    },
    data () {
        return {
            messages: [],
            newMessage: '',
            isLoading: false,
            sessionId: null,
            flightDuration: null,
            altitudeRange: null,
            batteryRange: null
        }
    },
    computed: {
        hasFlightData () {
            return Object.keys(this.flightData).length > 0
        }
    },
    methods: {
        async sendMessage () {
            if (!this.newMessage.trim() || this.isLoading || !this.hasFlightData) return

            const userMessage = this.newMessage
            this.newMessage = ''
            this.isLoading = true

            this.messages.push({
                role: 'user',
                content: userMessage
            })

            try {
                const response = await axios.post('http://localhost:8001/chat', {
                    message: userMessage,
                    sessionId: this.sessionId
                })

                this.messages.push({
                    role: 'assistant',
                    content: response.data.response
                })

                this.$nextTick(() => {
                    const container = this.$refs.messageContainer
                    container.scrollTop = container.scrollHeight
                })
            } catch (error) {
                console.error('Error sending message:', error)
                this.messages.push({
                    role: 'assistant',
                    content: 'Sorry, there was an error processing your message.'
                })
            } finally {
                this.isLoading = false
            }
        },

        formatDuration (seconds) {
            const minutes = Math.floor(seconds / 60)
            const remainingSeconds = Math.floor(seconds % 60)
            return `${minutes}m ${remainingSeconds}s`
        },

        updateFlightInfo () {
            if (!this.hasFlightData) return

            if (this.flightData.GPS && this.flightData.GPS.length > 0) {
                const gpsData = this.flightData.GPS
                this.flightDuration = gpsData[gpsData.length - 1].timestamp - gpsData[0].timestamp
            }

            if (this.flightData.ATT && this.flightData.ATT.length > 0) {
                const altitudes = this.flightData.ATT
                    .map(msg => msg.alt)
                    .filter(alt => alt !== undefined)
                if (altitudes.length > 0) {
                    const min = Math.min(...altitudes)
                    const max = Math.max(...altitudes)
                    this.altitudeRange = `${min.toFixed(1)}m - ${max.toFixed(1)}m`
                }
            }

            if (this.flightData.BAT && this.flightData.BAT.length > 0) {
                const voltages = this.flightData.BAT
                    .map(msg => msg.volt)
                    .filter(volt => volt !== undefined)
                if (voltages.length > 0) {
                    const min = Math.min(...voltages)
                    const max = Math.max(...voltages)
                    this.batteryRange = `${min.toFixed(1)}V - ${max.toFixed(1)}V`
                }
            }
        }
    },
    watch: {
        flightData: {
            handler (newData) {
                if (newData && Object.keys(newData).length > 0) {
                    this.updateFlightInfo()

                    if (this.messages.length === 0) {
                        this.messages.push({
                            role: 'assistant',
                            content: 'Flight data loaded! You can ask me questions about your flight, such as:\n' +
                      '- What was the highest altitude reached?\n' +
                      '- When did the GPS signal first get lost?\n' +
                      '- What was the maximum battery temperature?\n' +
                      '- How long was the total flight time?\n' +
                      '- List all critical errors that happened mid-flight.\n' +
                      '- When was the first instance of RC signal loss?'
                        })
                    }
                }
            },
            immediate: true
        }
    },
    mounted () {
        this.sessionId = Date.now().toString()
    }
}
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f5f5f5;
  border-radius: 8px;
  overflow: hidden;
}

.chat-header {
  padding: 15px;
  background: #007bff;
  color: white;
}

.chat-header h3 {
  margin: 0;
  margin-bottom: 10px;
}

.flight-info {
  display: flex;
  gap: 15px;
  font-size: 0.9em;
}

.info-item {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.message {
  margin-bottom: 15px;
  max-width: 80%;
}

.message.user {
  margin-left: auto;
}

.message-content {
  padding: 10px 15px;
  border-radius: 15px;
  background: white;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
  white-space: pre-line;
}

.message.user .message-content {
  background: #007bff;
  color: white;
}

.message.assistant .message-content {
  background: white;
}

.chat-input {
  display: flex;
  padding: 15px;
  background: white;
  border-top: 1px solid #eee;
}

.chat-input input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-right: 10px;
}

.chat-input button {
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.chat-input button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
