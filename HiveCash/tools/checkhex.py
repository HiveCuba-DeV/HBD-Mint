def checkhex(data: list | str):
    if not data:
        return False
    try:
        for c in data:
            if c != bytes.fromhex(c).hex():
                return False
        return True

    except:
        return False
