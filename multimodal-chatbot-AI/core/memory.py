class ChatMemory:
    """Keeps the last N messages of one conversation, plus an uploaded document (if any)."""

    def __init__(self, max_messages=20):
        self.max_messages = max_messages
        self.messages = []
        self.document = None      # DocumentStore from module8

    def add(self, role, content):
        self.messages.append({"role": role, "content": content})
        self.messages = self.messages[-self.max_messages:]
        while self.messages and self.messages[0]["role"] != "user":
            self.messages.pop(0)

    def get(self):
        return list(self.messages)

    def clear(self):
        self.messages = []
        self.document = None
