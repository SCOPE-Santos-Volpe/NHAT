import generate_hin
import multiprocessing as mp

state_ids = [i for i in range(60)]
county_ids = [i for i in range(1000)]

if __name__=="__main__":
    params = []
    for state in state_ids:
        for county in county_ids:
            params.append((state,county,'FARS','NONE'))
            # theoretically this should work

    with mp.Pool() as pool:
        pool.starmap(generate_hin.generate_hin_single_county, params, chunksize=1)