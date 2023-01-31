class PathConverter:
    #regex = '[-/\w]*\w'
    regex = '[-/a-zA-Z\d]+'
    #^so I just removed the '_' from the possible page_path characters since otherwise it matched the "_update"'s (too greedy)

    def to_python(self, value):
        print(value)
        return str(value)

    def to_url(self, value):
        return str(value)
