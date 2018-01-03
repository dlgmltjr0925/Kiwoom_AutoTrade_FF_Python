import configparser
config = configparser.ConfigParser()
config.sections() # 섹션 정보를 불러옴[]
print("config.section() :", config.sections()) # []
print('read(config.section())')
config.read('example.ini') # read 설정파일을 불러옴
print("config.section() :", config.sections()) # ['bitbucket.org', 'topsecret.server.com']
print('bitbucket.org' in config) # 존재하면 True
print('bitbucket.com' in config) # 존재하지 않으면 False
print(config['bitbucket.org']['User']) # hg
print(config['DEFAULT']['Compression']) # yes
topsecret = config['topsecret.server.com']
print(topsecret['forwardX11']) # 대소문자 상관 없음
print(topsecret['Port'])
for key in config['bitbucket.org']:
    print(key)

print(type(int(topsecret['Port'])))
print(type(float(topsecret['CompressionLevel'])))
print(topsecret.getboolean('ForwardX11'))
print(config['bitbucket.org'].getboolean('ForwardX11'))
print(config.getboolean('bitbucket.org', 'Compression'))
print(type(topsecret.get('Port')))
print(type(topsecret['Port']))
print(topsecret.get('CompressionLevel'))
print(topsecret.get('Chiper'))
print(topsecret.get('Chiper', '3des-cbc'))
print(topsecret.get('CompressionLevel', '3'))
print(config.get('bitbucket.org', 'monster', fallback = 'No such things as monsters'))
print('BatchMode' in topsecret)
print(topsecret.getboolean('BatchMode', fallback = True))
config['DEFAULT']['BatchMode'] = 'no'
print(topsecret.getboolean('BatchMode', fallback = True))


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
