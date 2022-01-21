opcodes = {
  OP_0: 0x00,
  OP_PUSHDATA1: 0x4c,
  OP_PUSHDATA2: 0x4d,
  OP_PUSHDATA4: 0x4e,
  // continue with the rest of opcodes, grab from https://github.com/bcoin-org/bcoin/blob/master/lib/script/common.js
};

codeops = Object.keys(opcodes).reduce(function(o, k) { 
  o[opcodes[k]] = k; return o;
},{})

function bytesToHexString(bytearray) { return bytearray.reduce(function(o, c) { return o += ('0' + (c & 0xFF).toString(16)).slice(-2)},'' ) }

function hexStringToBytes(script) { 
  return script.split('').reduce(function(o,c,i) {
    if(i%2===0) o.push(c)
    else o[o.length-1]+=c
    return o
  }, []).map(function(b) { return parseInt(b, 16)})
}

function asmToBytes(asm) {
  return asm.split(' ').reduce(function(o,c,i) { 
    if(typeof opcodes[c]!='undefined') { o.push(opcodes[c]); return o }
    else {
      var bytes = hexStringToBytes(c)
      if(bytes.length == 1 && bytes[0] > 1 && bytes[0] <= 16) {o.push(bytes[0]+0x50); return o}
      else if (bytes[0] < 0x02) { o.push(bytes[0]); return o}
      return o.concat( [bytes.length] ).concat(bytes)
    }
    
  },[])
}

function bytesToAsm(bytes) {
  var commands = []
  
  for(var b=0;b<bytes.length;b++) {
    var byte = bytes[b]
    if(byte <0x02) {
      commands.push(byte)
      continue
    }
    if(byte >= 0x52 && byte <= 0x60)  {
      commands.push(byte-0x50)
      continue
    }
    if(byte >= 0x02 && byte <= 0x4b) {
      commands.push(bytesToHexString(bytes.slice(b+1, b+1+byte)))
      b+=byte
      continue
    }
    if(codeops[byte]) commands.push(codeops[byte])
    else throw('unknown opcode'+byte+' '+b)
  }
  return commands
}
// usage
var redeem = "0020439e7a8753070e2c276da1e2ba02b7283e82d716196c3a52ccdb29536de242f9"
var witness = "0021022ff5be117c379c1d3ff245ff1309e1dd1e939384a0b1dd7d59db0a01b3920f13210366096ba1b9e3bbc13f66832ca825a1504c9b08124368eafe3741a0145719c159537a63777cb275ac677577ac68"
var asm = bytesToAsm(hexStringToBytes(witness)).join(' ')

console.log('redeem          ', bytesToAsm(hexStringToBytes(redeem)).join(' '))
console.log('witness         ', asm)
console.log('bytes equal?    ', asmToBytes(asm).join() == hexStringToBytes(witness).join()) 
console.log('strings equal?  ', bytesToHexString(asmToBytes(asm))==witness)