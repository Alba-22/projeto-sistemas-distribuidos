from socket import socket as s

def decide_chord(identifier: str, chord_1_socket: s, chord_2_socket: s) -> s:
    """Return chord index to insert a given ID"""
    if int(identifier) % 2 == 0:
        return chord_1_socket
    return chord_2_socket
