from safetext import SafeText
st = SafeText(language="en")

def check_profanity(text):
    """
    Checks if the text contains profanity.
    """
    if st.check_profanity(text):
        return True
    return False