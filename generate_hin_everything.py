import generate_hin
import multiprocessing as mp

def generate_all_hin_maps():
    # state_ids = [i for i in range(60)]
    state_ids = [i for i in range (60)]
    state_ids.remove(6)
    state_ids.remove(25)
    county_ids = [i for i in range(1000)]

    params = []

    # Sweep for non-SDS states
    for state in state_ids:
        for county in county_ids:
            params.append((state,county,'FARS','NONE'))

    # State 6 (CA)
    for county in county_ids:
        params.append(6,county,'SDS','California')

    # State 25 (MA)
    for county in county_ids:
        params.append(25,county,'SDS','Massachusetts')

    with mp.Pool() as pool:
        pool.starmap(generate_hin.generate_hin_single_county, params, chunksize=1)

if __name__=="__main__":
    generate_all_hin_maps()