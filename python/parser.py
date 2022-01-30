# -*- coding: utf-8 -*-
#
# Blockchain parser
# Copyright (c) 2015-2021 Denis Leonov <466611@gmail.com>
#
import atexit
import psycopg2

import os
import datetime
import hashlib

conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="postgres")
cursor = conn.cursor()


@atexit.register
def goodbye():
    cursor.close()
    conn.close()
    print('You are now leaving the Python sector.')


def insertBlock(magic_number, block_size, previus_block_hash, version_number, merkleroot_hash, timestamp, difficulty, random_number, transactions_count, current_block_hash):
    cursor.execute('INSERT INTO block VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (magic_number, block_size, previus_block_hash,
                   version_number, merkleroot_hash, timestamp, difficulty, random_number, transactions_count, current_block_hash))
    conn.commit()


def insertTransaction(version_number, inputs_count, outputs_count, lock_time, tx_hash, block_hash):
    cursor.execute('INSERT INTO transaction VALUES (%s,%s,%s,%s,%s,%s)',
                   (version_number, inputs_count, outputs_count, lock_time, tx_hash, block_hash))
    conn.commit()


def insertInput(tx_from_hash, n_output, input_script, sequence_number, tx_hash):
    cursor.execute('INSERT INTO input VALUES (%s,%s,%s,%s,%s)',
                   (tx_from_hash, n_output, input_script, sequence_number, tx_hash))
    conn.commit()


def insertOutput(value, output_script, tx_hash):
    cursor.execute('INSERT INTO output VALUES (%s,%s,%s)',
                   (value, output_script, tx_hash))
    conn.commit()


def insertWitness(witness, tx_hash):
    cursor.execute('INSERT INTO witness VALUES (%s,%s,%s)',
                   (witness, tx_hash))
    conn.commit()


def reverse(input):
    L = len(input)
    if (L % 2) != 0:
        return None
    else:
        Res = ''
        L = L // 2
        for i in range(L):
            T = input[i*2] + input[i*2+1]
            Res = T + Res
            T = ''
        return (Res)


def merkleRoot(lst):  # https://gist.github.com/anonymous/7eb080a67398f648c1709e41890f8c44
    def sha256d(x): return hashlib.sha256(hashlib.sha256(x).digest()).digest()
    def hash_pair(x, y): return sha256d(x[::-1] + y[::-1])[::-1]
    if len(lst) == 1:
        return lst[0]
    if len(lst) % 2 == 1:
        lst.append(lst[-1])
    return merkleRoot([hash_pair(x, y) for x, y in zip(*[iter(lst)]*2)])


def read_bytes(file, n, byte_order='L'):
    data = file.read(n)
    if byte_order == 'L':
        data = data[::-1]
    data = data.hex().upper()
    return data


def read_varint(file):
    b = file.read(1)
    bInt = int(b.hex(), 16)
    c = 0
    data = ''
    if bInt < 253:
        c = 1
        data = b.hex().upper()
    if bInt == 253:
        c = 3
    if bInt == 254:
        c = 5
    if bInt == 255:
        c = 9
    for j in range(1, c):
        b = file.read(1)
        b = b.hex().upper()
        data = b + data
    return data


dirA = 'D:/bitcoin/blocks/'  # Directory where blk*.dat files are stored
#dirA = sys.argv[1]
dirB = 'C:/result/'  # Directory where to save parsing results
#dirA = sys.argv[2]

fList = os.listdir(dirA)
fList = [x for x in fList if (x.endswith('.dat') and x.startswith('blk'))]

fListDirB = os.listdir(dirB)
fListDirB.sort()
noOfResultFiles = fListDirB.__len__()
fList = fList[noOfResultFiles::]
print('Continuing from ' + str(noOfResultFiles) +
      ' in ' + str(datetime.datetime.now()))

fList.sort()

for i in fList:
    nameSrc = i
    nameRes = nameSrc.replace('.dat', '.txt')
    resList = []
    a = 0
    t = dirA + nameSrc
    resList.append('Start ' + t + ' in ' + str(datetime.datetime.now()))
    print('Start ' + t + ' in ' + str(datetime.datetime.now()))
    f = open(t, 'rb')
    tmpHex = ''
    fSize = os.path.getsize(t)
    while f.tell() != fSize:
        magic_number = read_bytes(f, 4)
        resList.append('Magic number = ' + magic_number)
        block_size = read_bytes(f, 4)
        resList.append('Block size = ' + block_size)
        tmpPos3 = f.tell()
        tmpHex = read_bytes(f, 80, 'B')
        tmpHex = bytes.fromhex(tmpHex)
        tmpHex = hashlib.new('sha256', tmpHex).digest()
        tmpHex = hashlib.new('sha256', tmpHex).digest()
        tmpHex = tmpHex[::-1]
        current_block_hash = tmpHex.hex().upper()
        resList.append(
            'SHA256 hash of the current block hash = ' + current_block_hash)
        f.seek(tmpPos3, 0)
        version_number = read_bytes(f, 4)
        resList.append('Version number = ' + version_number)
        previus_block_hash = read_bytes(f, 32)
        resList.append(
            'SHA256 hash of the previous block hash = ' + previus_block_hash)
        print(previus_block_hash)
        merkleroot_hash = read_bytes(f, 32)
        resList.append('MerkleRoot hash = ' + merkleroot_hash)
        timestamp = read_bytes(f, 4)
        resList.append('Time stamp = ' + timestamp)
        difficulty = read_bytes(f, 4)
        resList.append('Difficulty = ' + difficulty)
        random_number = read_bytes(f, 4)
        resList.append('Random number = ' + random_number)
        tmpHex = read_varint(f)
        transactions_count = int(tmpHex, 16)
        resList.append('Transactions count = ' + str(transactions_count))
        resList.append('')
        tmpHex = ''
        RawTX = ''
        tx_hashes = []
        insertBlock(magic_number, block_size, previus_block_hash, version_number, merkleroot_hash,
                    timestamp, difficulty, random_number, transactions_count, current_block_hash)
        for k in range(transactions_count):
            tx_version_number = read_bytes(f, 4)
            resList.append('TX version number = ' + tx_version_number)
            RawTX = reverse(tx_version_number)
            tmpHex = ''
            Witness = False
            b = f.read(1)
            tmpB = b.hex().upper()
            bInt = int(b.hex(), 16)
            if bInt == 0:
                tmpB = ''
                f.seek(1, 1)
                c = 0
                c = f.read(1)
                bInt = int(c.hex(), 16)
                tmpB = c.hex().upper()
                Witness = True
            c = 0
            if bInt < 253:
                c = 1
                tmpHex = hex(bInt)[2:].upper().zfill(2)
                tmpB = ''
            if bInt == 253:
                c = 3
            if bInt == 254:
                c = 5
            if bInt == 255:
                c = 9
            for j in range(1, c):
                b = f.read(1)
                b = b.hex().upper()
                tmpHex = b + tmpHex
            inputs_count = int(tmpHex, 16)
            resList.append('Inputs count = ' + str(inputs_count))
            tmpHex = tmpHex + tmpB
            RawTX = RawTX + reverse(tmpHex)
            for m in range(inputs_count):
                tx_from_hash = read_bytes(f, 32)
                resList.append('TX from hash = ' + tx_from_hash)
                RawTX = RawTX + reverse(tmpHex)
                n_output = read_bytes(f, 4)
                resList.append('N output = ' + n_output)
                RawTX = RawTX + reverse(tmpHex)
                tmpHex = ''
                b = f.read(1)
                tmpB = b.hex().upper()
                bInt = int(b.hex(), 16)
                c = 0
                if bInt < 253:
                    c = 1
                    tmpHex = b.hex().upper()
                    tmpB = ''
                if bInt == 253:
                    c = 3
                if bInt == 254:
                    c = 5
                if bInt == 255:
                    c = 9
                for j in range(1, c):
                    b = f.read(1)
                    b = b.hex().upper()
                    tmpHex = b + tmpHex
                scriptLength = int(tmpHex, 16)
                tmpHex = tmpHex + tmpB
                RawTX = RawTX + reverse(tmpHex)
                input_script = read_bytes(f, scriptLength, 'B')
                resList.append('Input script = ' + input_script)
                RawTX = RawTX + tmpHex
                sequence_number = read_bytes(f, 4, 'B')
                resList.append('Sequence number = ' + sequence_number)
                RawTX = RawTX + tmpHex
                tmpHex = ''
                insertInput(tx_from_hash, n_output, input_script,
                            sequence_number, tx_hash)
            b = f.read(1)
            tmpB = b.hex().upper()
            bInt = int(b.hex(), 16)
            c = 0
            if bInt < 253:
                c = 1
                tmpHex = b.hex().upper()
                tmpB = ''
            if bInt == 253:
                c = 3
            if bInt == 254:
                c = 5
            if bInt == 255:
                c = 9
            for j in range(1, c):
                b = f.read(1)
                b = b.hex().upper()
                tmpHex = b + tmpHex
            outputs_count = int(tmpHex, 16)
            tmpHex = tmpHex + tmpB
            resList.append('Outputs count = ' + str(outputs_count))
            RawTX = RawTX + reverse(tmpHex)
            for m in range(outputs_count):
                tmpHex = read_bytes(f, 8)
                value = tmpHex
                RawTX = RawTX + reverse(tmpHex)
                tmpHex = ''
                b = f.read(1)
                tmpB = b.hex().upper()
                bInt = int(b.hex(), 16)
                c = 0
                if bInt < 253:
                    c = 1
                    tmpHex = b.hex().upper()
                    tmpB = ''
                if bInt == 253:
                    c = 3
                if bInt == 254:
                    c = 5
                if bInt == 255:
                    c = 9
                for j in range(1, c):
                    b = f.read(1)
                    b = b.hex().upper()
                    tmpHex = b + tmpHex
                scriptLength = int(tmpHex, 16)
                tmpHex = tmpHex + tmpB
                RawTX = RawTX + reverse(tmpHex)
                output_script = read_bytes(f, scriptLength, 'B')
                resList.append('Value = ' + value)
                resList.append('Output script = ' + output_script)
                RawTX = RawTX + tmpHex
                tmpHex = ''
                insertOutput(value, output_script, tx_hash)
            if Witness == True:
                for m in range(inputs_count):
                    tmpHex = read_varint(f)
                    WitnessLength = int(tmpHex, 16)
                    for j in range(WitnessLength):
                        tmpHex = read_varint(f)
                        WitnessItemLength = int(tmpHex, 16)
                        tmpHex = read_bytes(f, WitnessItemLength)
                        witness = str(m) + ' ' + str(j) + ' ' + \
                            str(WitnessItemLength) + ' ' + tmpHex
                        resList.append('Witness ' + witness)
                        tmpHex = ''
                        insertWitness(witness, tx_hash)
            Witness = False
            lock_time = read_bytes(f, 4)
            resList.append('Lock time = ' + lock_time)
            RawTX = RawTX + reverse(tmpHex)
            tmpHex = RawTX
            tmpHex = bytes.fromhex(tmpHex)
            tmpHex = hashlib.new('sha256', tmpHex).digest()
            tmpHex = hashlib.new('sha256', tmpHex).digest()
            tmpHex = tmpHex[::-1]
            tx_hash = tmpHex.hex().upper()
            resList.append('TX hash = ' + tx_hash)
            tx_hashes.append(tmpHex)
            resList.append('')
            tmpHex = ''
            RawTX = ''
            insertTransaction(version_number, inputs_count,
                              outputs_count, lock_time, tx_hash, current_block_hash)
        a += 1
        tx_hashes = [bytes.fromhex(h) for h in tx_hashes]
        tmpHex = merkleRoot(tx_hashes).hex().upper()
        if tmpHex != merkleroot_hash:
            print('Merkle roots does not match! >', merkleroot_hash, tmpHex)
    f.close()
    f = open(dirB + nameRes, 'w')
    for j in resList:
        f.write(j + '\n')
    f.close()
