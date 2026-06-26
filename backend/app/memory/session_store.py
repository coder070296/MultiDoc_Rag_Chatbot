from typing import Dict, List


SESSION_MEMORY: Dict[str, List[dict]] = {}


def get_chat_history(session_id: str) -> List[dict]:
    return SESSION_MEMORY.get(session_id, [])


def add_message(session_id: str, role: str, content: str):
    if session_id not in SESSION_MEMORY:
        SESSION_MEMORY[session_id] = []

    SESSION_MEMORY[session_id].append(
        {
            "role": role,
            "content": content,
        }
    )

    SESSION_MEMORY[session_id] = SESSION_MEMORY[session_id][-10:]


def format_chat_history(session_id: str) -> str:
    history = get_chat_history(session_id)

    if not history:
        return "No previous conversation."

    return "\n".join(
        [
            f"{message['role'].upper()}: {message['content']}"
            for message in history
        ]
    )


def clear_session(session_id: str):
    SESSION_MEMORY.pop(session_id, None)


def clear_all_sessions():
    SESSION_MEMORY.clear()