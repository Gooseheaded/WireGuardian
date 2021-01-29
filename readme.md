# WireGuardian

A stupid simple python script to help wireguard peering.

## Notes

This script is *stupid simple* and not robust whatsoever. CIDRs are not validated, the private key is stored plainly in `wireguardian.ini`, the fake 'DHCP' does not wrap around 255, etc.

As the 'server', you just need to run `wireguardian.py server` on a terminal (read below, 'Usage'). Only you need to run WireGuardian.

For your 'clients', a flask webserver is included, so they can interact with WireGuardian through a browser. Peers do not need to run WireGuardian.

## Installation

On Linux:
```
$ python3 -m venv flask
$ . venv/bin/activate
$ pip install Flask
```

On Windows (PowerShell):
```
$ python3 -m venv flask
$ venv/Scripts/activate
$ pip install Flask
```

## Usage

First, you need to create an initial configuration for this instance of WireGuardian:
```
$ python3 ./wireguardian.py server
```

That should generate the `config.ini` and `wireguardian.ini` files for you. Your wireguard config file is `config.ini`.

Now, you activate the virtualenv and run Flask:
```
$ flask run
```

You now have a webserver running on port 5000. Your peers can now go to http://your-ip-address:5000/wireguard , where they can submit their public keys. WireGuardian will generate the wg config files for you and your peers.

Your peer's wireguard config file will be returned as HTML to them, and a copy is also stored in your logs (`wireguardian_logs.txt`).