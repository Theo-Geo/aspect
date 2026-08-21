#%%
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 21:18:56 2026

@author: theoh
"""

import numpy as np 
import pickle
from matplotlib import pyplot as plt 

class stats:
    def __init__(self, path2stat:str):
        #loading stats for some reason
        self.path2stat = path2stat
        self.stats = np.genfromtxt(self.path2stat, 
                                   comments="#", dtype=None, delimiter=None, 
                                   encoding="utf-8", filling_values=np.nan)
        col_names = self.stats.dtype.names
        self.columns = dict()

        file = open(self.path2stat, "r")
        for col_name in col_names: 
            line = file.readline()
            delim_pos = line.find(":")
            self.columns[line[delim_pos+2:].replace("\n", "")] = col_name
        file.close()
        print("keys in your stat file:", self.columns.keys())
        
        self.time_steps = self.stats[self.columns["Time step number"]]
        self.time = self.stats[col_names[1]]
        self.time_dt = self.stats[col_names[2]]
    
    def read_column(self, column_name): 
        return self.stats[self.columns[column_name]]

#%% import mean top velocity rathmann 
output_names = ["isotropic-plastic-quat", "isotropic-viscoplastic-quat", "anisotropic-viscoplastic-quat-lin"]

stat_files =  [stats("../plugin/output-tosi-" + app + "/statistics") 
                   for i, app in enumerate(output_names)]

#%% import mean top velocity models 


loc_rathmann = "../data_rathmann_2024/"
data_rathmann = [pickle.load(open(loc_rathmann + name + ".pkl", 'rb'))
                  for name in ["summary-plastic",
                               "summary-isotropic-viscoplastic",
                               "summary-orthotropic-viscoplastic"]]

#%%

fig, axvmean = plt.subplots(1,1, figsize=(5,4), dpi=400, layout="tight")

axerr = axvmean.inset_axes([0,1.1, 1, 0.5], sharex=axvmean)
axvmean.set(xlabel="t", ylabel="mean top velocity",
            xlim=(0,0.2), ylim=(0,450))
axvmean.set_xticks(np.linspace(0, 0.2, 11), minor=True)
axvmean.set_xticks(np.linspace(0, 0.2, 6))
axerr.set(yscale="log", ylabel="rel diff.", ylim=(1e-3,2))
axerr.tick_params(labelbottom=False, right=True)

for i, stat, data, color, label in zip(np.arange(3), stat_files, data_rathmann,
                          ["black","#936f1fff","#91c673ff"], 
                          ["plastic", "isotropic viscoplastic", 
                           "orthotropic viscoplastic"]): 
    meanx_vel = stat.read_column("RMS velocity on boundary " + 
                                 "with indicator 3 (\"top\") (m/s)")
    axvmean.plot(stat.time, meanx_vel, ls="-", lw=1.2, c=color,label=label)
    # plot data from rathmann 2024
    meanx_vel_rthm = data["uxavg"]
    axvmean.plot(data["t"], meanx_vel_rthm, ls="--", c=color, lw=1.2)
    
    meanx_vel_interp = np.interp(data["t"] , stat.time, meanx_vel)
    rel_error = np.abs(meanx_vel_interp - meanx_vel_rthm)/meanx_vel_rthm
    
    axerr.plot(data["t"], rel_error, ls = "-", lw=1.2, c=color)
    
axerr.axhline(1e-2, ls="--",c="k", alpha=0.5, lw=1.2)
axerr.axhline(1e-1, ls="--",c="k", alpha=0.5, lw=1.2)

axvmean.plot(-1,0, "--", c="#91c673ff", label="Rathmann 2024")

axvmean.legend(loc="upper right", frameon=False)

plt.savefig("tosi_rathmann_time_series.png", 
            bbox_inches = 'tight')


