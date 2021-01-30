import sys
import configparser
import os.path
from datetime import datetime
from collections import OrderedDict

wgConfFileName = 'wireguardian.conf'

def __rtfm():
    print('WireGuardian')
    print('version 1.0.0')
    print('')
    print('Usage:')
    print('wireguardian init\t\tConfigure this wireguardian so that peers can connect to you.')
    print(
        'wireguardian client [publickey]\t\tCreate a wg conf file for a peer.')


def __log(message):
    with open('wireguardian_logs.txt', 'a') as log:
        log.write(datetime.now().strftime('%H:%M:%S') + ' - ' + message + '\n')


def createServerConfig():
    __log('Creating new server configuration file.')

    print("You are now configuring wireguardian. Provide the data you want for your wireguard network:\n")
    # CIDR
    cidr = ''
    is_cidr_valid = False
    while not is_cidr_valid:
        cidr = input('Wireguard network CIDR (xxx.xxx.xxx.xxx/yy): ')
        is_cidr_valid = True
        # if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}$', cidr):
        #    print('ERROR: Invalid CIDR. A valid CIDR is xxx.xxx.xxx.xxx/yy')

    # Port
    port = 0
    is_port_valid = False
    while not is_port_valid:
        port = input('Wireguard will listen on port: ')
        try:
            port = int(port)
        except:
            print('ERROR: Invalid port. Must be a number [0-65535].')
            continue
        if port < 0 or port > 65535:
            print('ERROR: Invalid port. Must be a number [0-65535].')
            continue
        is_port_valid = True

    # Endpoint
    endpoint = ''
    is_endpoint_valid = False
    while not is_endpoint_valid:
        endpoint = input('Your public endpoint (IP or URL) is: ')
        is_endpoint_valid = True

    # Private Key
    privkey = ''
    is_privkey_valid = False
    while not is_privkey_valid:
        privkey = input('Wireguard private key file name: ')
        if not os.path.exists(privkey):
            print('ERROR: File does not exist.')
            continue
        with open(privkey, 'r', encoding='utf-8') as f:
            privkey = f.readline()
        is_privkey_valid = True

    # Public key
    pubkey = ''
    is_pubkey_valid = False
    while not is_pubkey_valid:
        pubkey = input('Wireguard public key file name: ')
        if not os.path.exists(pubkey):
            print('ERROR: File does not exist.')
            continue
        with open(pubkey, 'r', encoding='utf-8') as f:
            pubkey = f.readline()
        is_pubkey_valid = True

    # Create the config file
    with open(wgConfFileName, 'w') as config:
        config.writelines(['[Interface]\n',
                           'Address = ' + str(cidr) + '\n',
                           'ListenPort = ' + str(port) + '\n',
                           'PrivateKey = ' + str(privkey)])

    with open('wireguardian.ini', 'w') as config:
        config.writelines(['[Data]\n',
                           'Endpoint = ' + str(endpoint) +
                           ':' + str(port) + '\n',
                           'PublicKey = ' + str(pubkey) + '\n',
                           'PrivateKey = ' + str(privkey)])

    __log('Created config.ini and wireguardian.ini.')
    return (wgConfFileName, 'wireguardian.ini')


peers = []


class __peerReader(OrderedDict):
    def __setitem__(self, key, val):
        if isinstance(val, dict) and key == 'Peer':
            peers.append(val)
        OrderedDict.__setitem__(self, key, val)


def createClientConfig(pubkey):
    if not os.path.exists(wgConfFileName):
        __log('[ERROR][createClientConfig]: Tried to create a client config for pubkey "' +
              pubkey + '", but this wireguardian has not been configured to serve clients yet.')
        return 'ERROR: This wireguardian has not been configured to serve clients yet.'

    config = configparser.ConfigParser(
        defaults=None, dict_type=__peerReader, strict=False)
    config.read(wgConfFileName)

    serverAddress = str(config['Interface']['Address'])
    serverAddress = serverAddress[:serverAddress.rindex('.')] + '.0/24'

    wireguardian = configparser.ConfigParser()
    wireguardian.read('wireguardian.ini')

    dhcp = 1
    for peer in peers:
        # If the 'new' peer already exists, simply echo back its config
        if peer['publickey'] == pubkey:
            existingConfig = ''
            existingConfig += '[Interface]' + '\n'
            existingConfig += 'Address = ' + peer['allowedips'] + '\n'
            existingConfig += 'PrivateKey = ***YOUR PRIVATE KEY HERE***' + '\n'
            existingConfig += '\n[Peer]' + '\n'
            existingConfig += 'AllowedIPs = ' + serverAddress + '\n'
            existingConfig += 'PublicKey = ' + \
                wireguardian['Data']['PublicKey'] + '\n'
            existingConfig += 'EndPoint = ' + \
                wireguardian['Data']['Endpoint'] + '\n'
            existingConfig += 'PersistentKeepAlive = 25' + '\n'
            __log('[INFO][createClientConfig]: Tried to create a client config, but a client with the pubkey "' +
                  pubkey + '" already exists (client address is ' + peer['allowedips'] + ').')
            __log(existingConfig)
            return existingConfig

        peerIP = peer['allowedips']
        peerIP = peerIP[peerIP.rindex('.') + 1:peerIP.rindex('/')]
        peerIP = int(peerIP)
        if peerIP > dhcp:
            dhcp = peerIP

    dhcp += 1
    newClientAddress = serverAddress[:serverAddress.rindex(
        '.') + 1] + str(dhcp) + '/32'

    newClientConfig = '[Interface]\n'
    newClientConfig += 'Address = ' + newClientAddress + '\n'
    newClientConfig += 'PrivateKey = ***YOUR PRIVATE KEY HERE***\n'
    newClientConfig += '\n[Peer]\n'
    newClientConfig += 'AllowedIPs = ' + serverAddress + '\n'
    newClientConfig += 'PublicKey = ' + \
        wireguardian['Data']['PublicKey'] + '\n'
    newClientConfig += 'EndPoint = ' + wireguardian['Data']['Endpoint'] + '\n'
    newClientConfig += 'PersistentKeepAlive = 25\n'

    newServerSection = '\n\n[Peer]\n'
    newServerSection += 'AllowedIPs = ' + newClientAddress + '\n'
    newServerSection += 'PublicKey = ' + str(pubkey)

    with open('config.ini', 'a') as config:
        config.write(newServerSection)

    __log('[INFO][createClientConfig]: Created a new client config for pubkey "' +
          pubkey + '" (client address is ' + newClientAddress + ').')
    __log(newClientConfig)
    return newClientConfig


def __main(argv):
    if argv[0] == 'client':
        if len(argv) < 2:
            __rtfm()
            return
        clientConfig = createClientConfig(argv[1])
        print(clientConfig)
    elif argv[0] == 'init':
        files = createServerConfig()
        print('wg server config created: ' + files[0])
        print('wireguardian config created: ' + files[1])
    else:
        __rtfm()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        __rtfm()
        exit(-1)
    __main(sys.argv[1:])
