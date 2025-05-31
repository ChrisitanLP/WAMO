from enum import Enum

class MessageType(str, Enum):
    TEXT = 'text'
    LOCATION = 'location'
    IMAGE = 'image'
    DOCUMENT = 'document'
    WEB_PAGE = 'web_page'

    @classmethod
    def to_list(cls):
        return [(type.value, type.name.replace('_', ' ').title()) for type in cls]
