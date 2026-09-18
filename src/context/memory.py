from dataclasses import dataclass, field

@dataclass(slots=True)
class ConversationMessage:
    role:str
    content: str 

@dataclass(slots=True)
class COnversationMemory:
    messages: list[ConversationMessage] = field(default_factory=list)

    def add(
            self,
            role : str,
            content : str,
    )->None:
        if not content.strip():
            return 

        self.messages.append(
            ConversationMessage(
                role = role,
                content = content.strip()
            )
        )

    def recent(
            self,
            max_messages : int = 6,

    )->list[ConversationMessage]:
        return self.messages[-max_messages:]

    def clear(self)->None:
        self.messages.clear()