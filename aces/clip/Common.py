# XML namespace variables
nsprefix = "aces"
nsuri = "http://www.oscars.org/aces/ref/acesmetadata"

# Remove the XML namespace URI
def normalize(name):
    if name[0] == "{":
        uri, tag = name[1:].split("}")
        return tag
    else:
        return name


