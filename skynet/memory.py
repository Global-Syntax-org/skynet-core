"""Conversation memory management for Skynet Core."""


class MemoryManager:
    """Simple conversation memory management

    max_history: if None or 0, keep unlimited history; otherwise trim to that many user+assistant entries.
    """

    def __init__(self, max_history: int | None = 10):
        self.conversation_history = []
        # None or 0 => unlimited
        self.max_history = None if (max_history is None or max_history == 0) else int(max_history)

    def add_user_message(self, message: str):
        self.conversation_history.append({"role": "user", "content": message})
        self._trim_history()

    def add_assistant_message(self, message: str):
        self.conversation_history.append({"role": "assistant", "content": message})
        self._trim_history()

    def _trim_history(self):
        # If max_history is None, keep full history
        if self.max_history is None:
            return

        if len(self.conversation_history) > self.max_history * 2:  # *2 for user+assistant pairs
            self.conversation_history = self.conversation_history[-self.max_history * 2:]

    def get_conversation_history(self) -> str:
        if not self.conversation_history:
            return "No conversation history yet."

        history = []
        for entry in self.conversation_history[-6:]:  # Last 3 exchanges
            role = entry["role"].title()
            content = entry["content"]
            history.append(f"{role}: {content}")

        return "\n".join(history)
