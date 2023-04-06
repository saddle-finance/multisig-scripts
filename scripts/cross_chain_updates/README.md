# Main process
1) collect veSDL data since last run from https://dune.com/queries/1400702, save as csv for step 2 (`csv/veSDL.csv`)
  - change timestamp in query to ts of last run (should be 1 week ago)
2) trigger root oracle push (--network mainnet)
3) trigger root gauge emissions (--network mainnet)
  - some gauges will fail if they have no weight. Copy those addresses (which will be logged to console) into the "bad_gauges" array in the next function
4) Confirm that emissions have all landed, may take 10-20 min
5) sidechains child gauge factory mints
  - make sure that bad_gauges were included from the previous step. 
  - not necessary to specify network when running.

## Timing
Wednesday AFTER 8pm EST

## trouble shooting:
- if a step fails, try increasing the gas

## example call:
`brownie run scripts/cross_chain_updates/mainnet_trigger_root_oracle_push.py --network mainnet`