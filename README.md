# CS3103-Assignment-4

## IMPORTANT
Before you run or setup a GameNetServer, you need to run the follow ssl command and put the cert and priv key into the root directory.

`openssl req -new -x509 -days 365 -nodes -out cert.pem -keyout key.pem`

Cert and priv keys are needed since QUIC uses TLS.

## Demo
1. In one terminal, run `python3 gameNetServer-demo.py` from the root directory.
2. In another terminal, run `python3 gameNetClient-demo.py`
3. You should see simultaneously both client and server printing the received data at the same time.

