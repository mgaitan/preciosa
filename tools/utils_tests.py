"""
utilidades para testing
"""

def _dump_response_on_file(response, filepath=None):
    """
    Useful when debugging responses.
    Calls to this function should not be committed.
    """
    if not filepath:
        from tempfile import mkstemp
        _, filepath = mkstemp(text=True)
    f = file(filepath, 'w')
    f.write(response.content)
    f.close()
    return filepath

def see(response):
    """ load the html of a response for debugging purposes

    Attention: Calls to this method should not be committed.
    """
    import webbrowser
    fpath = _dump_response_on_file(response)
    webbrowser.open_new_tab(fpath)