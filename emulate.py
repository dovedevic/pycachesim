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
        [2048, 4096, 4096*2],
        [4, 8, 16],
        32,
        level_latencies=[(2, 3),(10, 12),(50, 52), (100, 102)]
    )
    ###   Typically you change the above   ###

    print("Running trace...")
    for line in fp.readlines():
        # print(line.strip())
        address_type, operation, hex_address = line.split(' ')

        is_data_op = True if address_type == "D" else False
        method = simulate.perform_fetch if operation == "R" else simulate.perform_set
        int_address = int(hex_address, 16)

        method(int_address, for_data=is_data_op)

    print("Finished trace... Gathering metrics")
    simulate.stats.save('testing.out')
print("Done.")
