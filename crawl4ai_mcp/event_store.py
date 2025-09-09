"""
EventStore implementation for StreamableHTTP with correct signature.
Fixes the store_event() TypeError by matching the MCP SDK interface.
"""

from typing import Optional, Dict, List, Tuple, Callable, Any
import uuid
import logging

logger = logging.getLogger(__name__)


class CorrectEventStore:
    """
    EventStore implementation that matches MCP SDK's EventStore ABC.
    
    Fixes the TypeError: store_event() takes 2 positional arguments but 3 were given
    by implementing the correct method signature.
    """
    
    def __init__(self):
        # Store events as: {stream_id: [(event_id, message), ...]}
        self.events: Dict[str, List[Tuple[str, dict]]] = {}
        self.event_counter = 0
        logger.info("Initialized CorrectEventStore with proper signature")
    
    async def store_event(self, stream_id: str, message: dict) -> str:
        """
        Store an event for a specific stream.
        
        Args:
            stream_id: The ID of the stream this event belongs to
            message: The JSON-RPC message to store
            
        Returns:
            The generated event ID for this event
        """
        self.event_counter += 1
        event_id = f"evt_{self.event_counter:06d}"
        
        # Initialize stream if it doesn't exist
        if stream_id not in self.events:
            self.events[stream_id] = []
            logger.debug(f"Created new stream: {stream_id}")
        
        # Store the event
        self.events[stream_id].append((event_id, message))
        logger.debug(f"Stored event {event_id} for stream {stream_id}")
        
        return event_id
    
    async def replay_events_after(
        self, 
        last_event_id: str, 
        send_callback: Callable[[Dict[str, Any]], Any]
    ) -> Optional[str]:
        """
        Replay events after a specific event ID.
        
        This is used for resumability - when a client reconnects,
        it can request all events after the last one it received.
        
        Args:
            last_event_id: The ID of the last event the client received
            send_callback: Callback to send each event
            
        Returns:
            The stream_id if events were found and replayed, None otherwise
        """
        logger.debug(f"Attempting to replay events after {last_event_id}")
        
        # Find the stream and position of the last event
        for stream_id, events in self.events.items():
            for i, (event_id, message) in enumerate(events):
                if event_id == last_event_id:
                    # Found it! Replay all subsequent events
                    logger.info(f"Found event {last_event_id} in stream {stream_id} at position {i}")
                    
                    # Replay all events after this one
                    for future_event_id, future_message in events[i+1:]:
                        await send_callback({
                            "message": future_message,
                            "event_id": future_event_id
                        })
                        logger.debug(f"Replayed event {future_event_id}")
                    
                    return stream_id
        
        logger.warning(f"Event {last_event_id} not found in any stream")
        return None
    
    async def get_events(self, stream_id: Optional[str] = None) -> List[Tuple[str, dict]]:
        """
        Get all events for a stream (or all streams if stream_id is None).
        
        This is a helper method for debugging and testing.
        
        Args:
            stream_id: Optional stream ID to filter events
            
        Returns:
            List of (event_id, message) tuples
        """
        if stream_id:
            return self.events.get(stream_id, [])
        
        # Return all events from all streams
        all_events = []
        for stream_events in self.events.values():
            all_events.extend(stream_events)
        return all_events
    
    def clear(self):
        """Clear all stored events (useful for testing)."""
        self.events.clear()
        self.event_counter = 0
        logger.info("Cleared all events from store")


# Optional: Simple in-memory store without resumability
class SimpleEventStore:
    """
    Minimal EventStore for when resumability is not needed.
    Still implements the correct signature to avoid errors.
    """
    
    async def store_event(self, stream_id: str, message: dict) -> str:
        """Simply return a dummy event ID without storing."""
        return f"evt_{uuid.uuid4().hex[:8]}"
    
    async def replay_events_after(
        self, 
        last_event_id: str, 
        send_callback: Callable[[Dict[str, Any]], Any]
    ) -> Optional[str]:
        """No events to replay in simple mode."""
        return None