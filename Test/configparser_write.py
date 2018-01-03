import configparser
config = configparser.ConfigParser()
config['DEFAULT'] = {'ServerAliveInterval': '45',
                  'Compression': 'yes',
                  'CompressionLevel': '9'}
config['bitbucket.org'] = {}
config['bitbucket.org']['User'] = 'hg'
config['topsecret.server.com'] = {}
topsecret = config['topsecret.server.com']
topsecret['Port'] = '50022'     # mutates the parser
topsecret['ForwardX11'] = 'no'  # same here
config['DEFAULT']['ForwardX11'] = 'yes'
with open('example.ini', 'w') as configfile:
    config.write(configfile)

# [DEFAULT]
# serveraliveinterval = 45
# compression = yes
# compressionlevel = 9
# forwardx11 = yes
#
# [bitbucket.org]
# user = hg
#
# [topsecret.server.com]
# port = 50022
# forwardx11 = no
#
