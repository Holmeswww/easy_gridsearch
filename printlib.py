def print_(v="", progress = "", caption = ""):
    string = "#####"
    if progress != "" or caption != "":
        print(string+v+"$"+progress+"$"+caption+string)
    else:
        return
        # print(v)

def print_normal(v=None, progress = None, caption = None):
    if v is None:
        return
    print(v)
