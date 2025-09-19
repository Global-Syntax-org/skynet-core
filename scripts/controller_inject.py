#!/usr/bin/env python3
import sys
import struct

# Define the event variable as a placeholder for debugging
# Replace this with the actual structure or data expected by the script
event = struct.pack("10s", b"placeholder")

print(f"Event size: {sys.getsizeof(event)}")
print(f"Event content: {event}")