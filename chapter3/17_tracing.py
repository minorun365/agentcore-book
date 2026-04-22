from strands import Agent
from strands.telemetry import StrandsTelemetry

strands_telemetry = StrandsTelemetry()
strands_telemetry.setup_console_exporter()

agent = Agent()
agent("こんにちは")
