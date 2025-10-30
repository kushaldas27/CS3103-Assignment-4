# CS3103-Assignment-4

## IMPORTANT
Before you run or setup a GameNetServer, you need to run the follow ssl command and put the cert and priv key into the root directory.

`openssl req -new -x509 -days 365 -nodes -out cert.pem -keyout key.pem`

Cert and priv keys are needed since QUIC uses TLS.

## Demo
1. In the root directory, run `python3 -m venv venv`, then `source venv/bin/activate`
1. Run `pip3 install -r requirements.txt`
1. Run `openssl req -new -x509 -days 365 -nodes -out cert.pem -keyout key.pem`
1. Run `sudo python3 topology.py <delay_ms> <jitter_ms> <loss_percentage>`

