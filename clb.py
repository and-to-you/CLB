import hashlib

def clb(text, digits=512, secret_key="Rewrite this", memory_mb=16, rounds=100000):
    text_clean = text.replace("\r\n", "\n").replace("\r", "\n")
    key_bytes = secret_key.encode('utf-8')
    key_hex_int = int(key_bytes.hex(), 16)
    
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"

    sha3_256 = hashlib.sha3_256
    sha3_512 = hashlib.sha3_512
    

    salt_bytes = sha3_256(text_clean.encode('utf-8') + key_bytes).digest()
    current_hash_str = sha3_512(key_bytes + salt_bytes).hexdigest()
    

    for index, char in enumerate(text_clean):
        c_bytes = char.encode('utf-8')
        idx_bytes = str(index).encode('utf-8')
        curr_bytes = current_hash_str.encode('utf-8')
        if index % 2 == 0:
            mixer_input = curr_bytes + b"_" + idx_bytes + b"_" + c_bytes + b"_" + key_bytes
        else:
            mixer_input = key_bytes + b"_" + c_bytes + b"_" + idx_bytes + b"_" + curr_bytes
        current_hash_str = sha3_512(mixer_input).hexdigest()

    while len(current_hash_str) < digits:
        current_hash_str += sha3_512(current_hash_str.encode('utf-8')).hexdigest()
    current_hash_str = current_hash_str[:digits]
    
    memory_pool_size = (memory_mb * 1024 * 1024) // 128
    

    pool_state_str = current_hash_str
    mem_pool_bytes = []

    def _build_pool(state, size, k_bytes):
        arr = []
        for i in range(size):
            state = sha3_512(state.encode('utf-8') + b"_" + str(i).encode('utf-8') + b"_" + k_bytes).hexdigest()
            arr.append(state.encode('utf-8'))
        return state, arr
        
    pool_state_str, mem_pool_bytes = _build_pool(pool_state_str, memory_pool_size, key_bytes)
    current_hash_bytes = pool_state_str.encode('utf-8')

    for i in range(20000):
        mix_index = int(sha3_512(current_hash_bytes).hexdigest(), 16) % memory_pool_size
        mixer_input = current_hash_bytes + b"_" + mem_pool_bytes[mix_index] + b"_" + str(i).encode('utf-8')
        current_hash_bytes = sha3_512(mixer_input).hexdigest().encode('utf-8')
        mem_pool_bytes[mix_index] = current_hash_bytes
        
    sha_buffer = bytearray(digits + 1 + len(key_bytes))
    sha_buffer[digits] = 95
    sha_buffer[digits+1:] = key_bytes
    
    for i in range(rounds):
        sha_buffer[:digits] = current_hash_bytes[:digits]
        current_hash_bytes = sha3_512(sha_buffer).hexdigest().encode('utf-8')
        
        if i % 10000 == 0:
            val = int(current_hash_bytes[:8], 16)
            chaos_factor = (val * 1103515245 + 12345) & 0x7fffffff
            chaos_input = current_hash_bytes + b"_" + str(chaos_factor).encode('utf-8')
            current_hash_bytes = sha3_512(chaos_input).hexdigest().encode('utf-8')
            
        while len(current_hash_bytes) < digits:
            current_hash_bytes += sha3_512(current_hash_bytes).hexdigest().encode('utf-8')
        current_hash_bytes = current_hash_bytes[:digits]
            
    current_hash_str = hashlib.shake_256(current_hash_bytes).hexdigest(digits // 2)
    final_number = int(current_hash_str, 16) - key_hex_int
    
    is_negative = final_number < 0
    num = abs(final_number)
    res = []
    while num:
        res.append(chars[num % 36])
        num //= 36
    output_str = "".join(reversed(res))
    if is_negative:
        output_str = "-" + output_str
        
    return output_str
