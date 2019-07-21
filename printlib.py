def print_(v, progress = None, caption = None):
    string = "#####"
    if progress is not None or caption is not None:
        print(string+v+"$"+progress+"$"+caption+string)
    else:
        print(v)
