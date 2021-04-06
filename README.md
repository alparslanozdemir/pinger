# pinger
A raw socket implementation of standard ping command with python.

# Description
Creates raw socket and icmp ping packet. Sends this packet to destination address. listens socket for receiving echo reply.

If packet returns and this packet is type-0 (echo reply), program prints destination ip and "AKTIF!!".

If it not receives any packet or the packet received is not echo reply, it types destination ip and "AKTIF DEGIL.".
