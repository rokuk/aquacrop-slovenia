def a(temp_max, temp_min, Tbase, Tupp):
    temp_max = min(temp_max, Tupp)
    temp_max = max(temp_max, Tbase)

    temp_min = min(temp_min, Tupp)
    Tmean = (temp_max + temp_min) / 2
    Tmean = max(Tmean, Tbase)
    gdd = Tmean - Tbase
    return gdd