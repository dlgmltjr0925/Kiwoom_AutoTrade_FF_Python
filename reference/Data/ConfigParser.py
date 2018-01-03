class Empty(object):
    pass

class Config(object):
    def __init__(self, configFilename, debug = False):
        self.debug = debug
        self.filename = os.path.join(os.path.split(__file__)[0], configFilename)
        self.config = configparser.ConfigParser()
        self.config.optionxform = lambda option: option    # prevent the key value being lowercase
        self.config.read(self.filename)

        # set sections
        for section in self.config.sections():
            if self.debug:
                print("[%s]" % section)
            if not hasattr(self, section):
                setattr(self, section, Empty())
            current_section = getattr(self, section)
            # set values
            for option in self.config[section]:
                value = self.config.get(section, option)
                if self.debug:
                    print("%s = %s" % (option, value))
                setattr(current_section, option, getValue(value))

    def getValue(self, section, option):
        return getValue(self.config[section][option])

    def setValue(self, section, option, value):
        # set value
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config[section][option] = str(value)

        # set internal method
        if not hasattr(self, section):
            setattr(self, section, Empty())
        current_section = getattr(self, section)
        setattr(current_section, option, value)

    def save(self):
        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)
            print("Saved Config : " + self.filename)

    def getFilename(self):
        return self.filename
