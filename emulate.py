from hierarchies.three_level_suu_inclusive_cache_system import ThreeLevelSUUInclusiveCacheSystem as Cache
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
        [32768, 2097152, 16777216],
        [32, 1, 1],
        32
    )
    ###   Typically you change the above   ###

    print("Running trace...")
    for line in fp.readlines():
        print(line)
        address_type, operation, hex_address = line.split(' ')

        is_data_op = True if address_type == "D" else False
        method = simulate.perform_fetch if operation == "R" else simulate.perform_set
        int_address = int(hex_address, 16)

        method(int_address, data_fetch=is_data_op)
    print("Finished trace... Gathering metrics")
print("Done.")
