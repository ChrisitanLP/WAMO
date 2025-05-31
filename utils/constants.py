# utils/constants.py

DEFAULT_PROFILE_PIC_URL = 'https://cdn.playbuzz.com/cdn/913253cd-5a02-4bf2-83e1-18ff2cc7340f/c56157d5-5d8e-4826-89f9-361412275c35.jpg'
CHAT_STATUSES = [
    ('pendiente', 'Pendiente'),
    ('atendiendo', 'Atendiendo'),
    ('atendido', 'Atendido')
]
BATCH_SIZE = 100
REQUEST_TIMEOUT = 10
MESSAGE_STATUSES = [
    ('pending', 'Pending'),
    ('delete', 'Delete'),
    ('forwarded', 'Forwarded'),
    ('important', 'Important'),
    ('sent', 'Sent')
]

MESSAGE_TYPES = [
    'text',
    'image',
    'video',
    'audio',
    'document',
    'location',
    'contact',
]

DEFAULT_BATCH_SIZE = 100
REQUEST_TIMEOUT = 10