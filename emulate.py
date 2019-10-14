from hierarchies.three_level_suu_exclusive_bypassing_cache_system import ThreeLevelSUUExclusiveBypassingCacheSystem as Cache
from system.system import AddressSpace
import policies.replacement_policies
import sys, os

if len(sys.argv) < 2:
    raise ValueError("No trace file given. Aborting...")
elif len(sys.argv) > 2:
    raise ValueError("Unknown arguments given")
if not os.path.exists(sys.argv[1]):
    raise ValueError("Trace file: '{}' does not exist!".format(sys.argv[1]))

with open(sys.argv[1], 'r') as fp:
    print("Creating cache...")

    ### Typically you change the following ###
    simulate = Cache(
        AddressSpace.in64Bit,
        policies.replacement_policies.LRUReplacementPolicy(),
        [32768, 262144, 2097152],
        [8, 8, 16],
        32,
        level_latencies=[(4, 4),(12, 12),(30, 30), (100, 100)]
    )
    ###   Typically you change the above   ###

    print("Collecting metadata...")
    lines = 0
    fp2 = open(sys.argv[1], 'r')
    for line in fp2.readlines():
        lines += 1
    fp2.close()

    print("Running trace...")
    at = 0
    print('[' + '-' * 50 + '] 0', end='\r')
    for line in fp.readlines():
        try:
            # print(line.strip())
            at += 1
            r = line.strip().replace('\x00', '').split(' ')
            if len(r) != 3 or (r[0] != "D" and r[0] != "I") or (r[1] != "R" and r[1] != "W") or len(r[2]) < 5 or 'x' in r[2][2:] or r[2][0] == 'x':  # Prevent strange malformed output from c++
                continue
            address_type, operation, hex_address = line.strip().replace('\x00', '').split(' ')

            is_data_op = True if address_type == "D" else False
            method = simulate.perform_fetch if operation == "R" else simulate.perform_set
            int_address = int(hex_address, 16)
            method(int_address, for_data=is_data_op)

            if at % 10000 == 0:
                print('[' + '='*((at *100 // lines)//2) + '-'*(50 - ((at *100 // lines)//2)) + ']' + str(at), end='\r')
        except Exception as ex:
            print("Exception thrown while trying to parse line:")
            print("{}: {}".format(at, line.strip()))
            print("The exception was: {}".format(str(ex)))
            print("Aborting...")
            break

    print('[' + '=' * 50 + ']' + str(at))
    print("Finished trace... Gathering metrics")
    simulate.stats.save('testing.out')
print("Done.")
