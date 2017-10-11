import struct

MAX_NUMBER_OF_ITEMS = 255
header_fmt = "<d?BBBL"
header_size = struct.calcsize(header_fmt)

'''
d - timestamp           8
? - reset book flag     1
B - asks count          1
B - bids count          1
B - trades count        1
L - reserved            4
                    =  16
'''

item_fmt = '<dd'
item_size = struct.calcsize(item_fmt)

class HeaderMsg:
    def __init__(self, header):
        self.timemoment, self.resetbookflag, self.askN, self.bidN, self.tradeN, self.res = header

class Message:
    def __init__(self, timemoment=0, resetbookflag = True, asks=[], bids=[], trades=[]):
        self.timemoment = timemoment
        self.asks = asks
        self.bids = bids
        self.trades = trades
        self.resetbookflag = resetbookflag

def packHeader(timemoment, resetbookflag = True, asks=[], bids=[], trades=[]):
    # be care to check len(asks) & len(bids) < 256
    return struct.pack(header_fmt, timemoment, resetbookflag, len(asks), len(bids), len(trades), 0)

def unpackHeader(msg):
    return struct.unpack(header_fmt, msg[:header_size])

def packAmountPrice(ap):
    price, amount = ap
    return struct.pack(item_fmt, price, amount)

def packMsg(timemoment, resetbookflag = True, asks=[], bids=[], trades=[]):
    msg = packHeader(timemoment, resetbookflag, asks, bids, trades, 0)

    for ap in asks + bids + trades:
        msg += packAmountPrice(ap)

    return msg

def unpackItems(items):
    return [struct.unpack(item_fmt, items[x:x + item_size]) for x in range(0, len(items), item_size)]

def unpackMsg(msg):
    header = HeaderMsg(unpackHeader(msg))

    l, r = header_size, header_size + item_size * header.askN
    asks = unpackItems(msg[l:r])

    l, r = r, r + item_size * header.bidN
    bids = unpackItems(msg[l:r])

    l, r = r, r + item_size * header.tradeN
    trades = unpackItems(msg[l:r])

    return (header.timemoment, header.resetbookflag,
                     asks, bids, trades)

def mdMsgSplit(c):
    i = 0
    messages = []
    while i < len(c):
        header = unpackHeader(c[i:i+header_size])
        asks_bids_trades = header[2] + header[3] + header[4]
        tail_size_bytes = asks_bids_trades * item_size
        total_size = header_size + tail_size_bytes
        messages += [c[i:i+total_size]]
        i += total_size
    return messages

def unpackMsgs(rawmsgbytes):
    msgs = mdMsgSplit(rawmsgbytes)
    return map(unpackMsg, msgs)
