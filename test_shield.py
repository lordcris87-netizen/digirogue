"""Regression tests for blue pixel shield and non-pausing online reward pickups."""
import asyncio
import importlib
import json
import tempfile
from pathlib import Path
from aiohttp import ClientSession
from aiohttp.test_utils import TestServer

import server

class FakeWS:
    closed = False


def make_room():
    room = server.Room('GAMEX1')
    for id, name in [('one','Uno'),('two','Dos')]:
        room.add(id,name,FakeWS())
    a,b=room.players['one'],room.players['two']
    a['x']=room.drops[1]['x'];a['y']=room.drops[1]['y']
    b['x']=a['x']+230;b['y']=a['y']
    return room,a,b


def test_collect_and_other_keeps_playing():
    room,a,b=make_room()
    now=__import__('time').monotonic()
    a['last_input']=now;b['last_input']=now
    a['vx']=0.;b['vx']=1.
    a['hp']=43
    room.step(.1)
    assert a['shield'] is True
    assert len(room.drops)==0
    assert len(room.events)==1 and room.events[0][0]=='one'
    assert room.events[0][1]['type']=='reward_offer'
    assert len(room.events[0][1]['choices'])==3
    snap=room.snapshot()
    assert snap['players'][0]['shield'] is True
    assert snap['players'][1]['shield'] is False
    startx=a['x'];otherx=b['x'];starttime=room.elapsed
    # Attempt to move/attack when protected. Other player advances, time advances.
    a['vx']=1.;a['attack']=True
    room.step(.15)
    assert a['x']==startx
    assert a['hp']==43
    assert b['x']>otherx
    assert room.elapsed>starttime
    assert a['shield'] and a['reward_timer'] < server.REWARD_SECONDS
    # Enemy may attack other player, but not the shielded one.
    b['x']=a['x']+150;b['y']=a['y']
    room.enemies[100]=dict(id=100,x=a['x']+5,y=a['y'],hp=45,maxhp=45,
         speed=300.,type='kunemon',hit_cd=0.,facing=4)
    room.step(.2)
    assert a['hp']==43
    assert room.enemies[100]['x']>a['x']+5 # heads toward unshielded player
    # Can't spoof invalid option or replay.
    oid=a['reward_id'];rid=a['reward'][0]['id']
    assert not room.choose_reward('two',oid,rid)
    assert not room.choose_reward('one',oid+1,rid)
    assert not room.choose_reward('one',oid,'hacker_upgrade')
    assert room.choose_reward('one',oid,rid)
    assert not a['shield'] and not a['reward']
    assert not room.choose_reward('one',oid,rid)
    assert room.events[-1][1]['type']=='reward_applied'
    print('PASS: shield at pickup, no world pause, other movement, enemy AI, authoritative choice')


def test_timeout_and_two_shields():
    room,a,b=make_room()
    room.step(.05)
    assert a['shield']
    room.spawn_drop(b['x'],b['y'])
    room.step(.05)
    assert b['shield'] and a['shield']
    assert a['reward_id'] == b['reward_id'] # IDs are private to each player
    room.step(server.REWARD_SECONDS+.01)
    assert not a['shield'] and not b['shield']
    assert a['reward'] is None and b['reward'] is None
    assert sum(ev['type']=='reward_applied' for cid,ev in room.events)==2
    print('PASS: simultaneous pickups and automatic timeout unshield both players')


async def test_two_websocket_clients():
    with tempfile.TemporaryDirectory() as tmp:
        server.DB_PATH=Path(tmp)/'score.sqlite3'
        async with TestServer(server.create_app()) as site:
            async with ClientSession() as session:
                ws1=await session.ws_connect(str(site.make_url('/ws')))
                ws2=await session.ws_connect(str(site.make_url('/ws')))
                h1=await ws1.receive_json();h2=await ws2.receive_json()
                await ws1.send_json({'type':'create','name':'TestUno'})
                joined=await ws1.receive_json()
                assert joined['type']=='joined'
                await ws2.send_json({'type':'join','code':joined['code'],'name':'TestDos'})
                assert (await ws2.receive_json())['type']=='joined'
                room=server.ROOMS[joined['code']]
                p1=room.players[h1['id']];p2=room.players[h2['id']]
                p1['x']=room.drops[1]['x'];p1['y']=room.drops[1]['y']
                # Consume websocket until owner gets reward offer.
                got=None
                for _ in range(18):
                    m=await ws1.receive_json(timeout=3)
                    if m['type']=='reward_offer': got=m;break
                assert got is not None, 'pickup was not offered'
                assert len(got['choices'])==3
                assert p1['shield'] is True
                original_sec=room.elapsed
                await asyncio.sleep(.22)
                assert room.elapsed>original_sec
                await ws2.send_json({'type':'input','x':1,'y':0,'attack':True})
                previous_x=p2['x'];await asyncio.sleep(.22)
                assert p2['x']>previous_x
                # Check invalid upgrade attempts do not remove protection.
                await ws1.send_json({'type':'choose_reward','offer_id':got['offer_id'],'choice':'super_cheat'})
                denied=None
                for _ in range(10):
                    m=await ws1.receive_json(timeout=3)
                    if m['type']=='error':denied=m;break
                assert denied and 'no es válida' in denied['message']
                assert p1['shield']
                await ws1.send_json({'type':'choose_reward','offer_id':got['offer_id'],'choice':got['choices'][0]['id']})
                applied=None
                for _ in range(12):
                    m=await ws1.receive_json(timeout=3)
                    if m['type']=='reward_applied':applied=m;break
                assert applied and applied['offer_id']==got['offer_id']
                assert not p1['shield']
                await ws1.close();await ws2.close()
        print('PASS: two real WebSocket clients receive reward independently; room keeps ticking; server rejects spoofing')


async def main():
    test_collect_and_other_keeps_playing()
    test_timeout_and_two_shields()
    await test_two_websocket_clients()

if __name__=='__main__':asyncio.run(main())
