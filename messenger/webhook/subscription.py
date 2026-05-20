def verify(mode, token, challenge, verify_token):
    if mode == 'subscribe' and token and token == verify_token:
        return challenge
    return None
