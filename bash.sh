python scripts/generate_sms_geo_asc.py -fsms fsms_asc -geo geo_asc -geosms geosms_asc
python scripts/generate_sms_geo_desc.py -fsms fsms_desc -geo geo_desc -geosms geosms_desc
zcat geosms_asc | sort -k1,1n -k2,2n -k3,3n -S10% | gzip > geosms_asc_sorted
zcat geosms_desc | sort -k1,1n -k2,2n -k3,3n -S10% | gzip > geosms_desc_sorted
python scripts/merge_geo.py -geosms1 geosms_asc_sorted -geosms2 geosms_desc_sorted -geosmsoutput geosms_final
python scripts/find_neighbors.py -bsid bs -bsnei bsnei
