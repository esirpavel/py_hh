# coding: utf-8
'''
Created on 29 июня 2016 г.

@author: Pavel Esir
'''
fltSize = 'float32'

import py_hh as phh
import numpy as np
from numpy import random
import matplotlib.pylab as pl
from distribute_delays import getDelays

random.seed(0)
psn_seed = 0

SimTime = 300000.
h = 0.02
Tsim = int(SimTime/h)
recInt = 2000

w_ps = np.arange(2.15, 2.30, 0.02)
#w_ps = np.array([0.5, 1.0, 2.0])
nw = len(w_ps)

N = 100
Nneur = N*nw

tau_psc = 0.2   # ms
w_n = 1.3       # connection weight, pA
I0 = 5.27

rate = np.zeros(Nneur, dtype=fltSize) + 185.0    # Poisson noise rate, Hz (shouldn't  be 0)

Ncon = int(N*N*0.2)
#Ncon = int(N*N)
pre = np.zeros(Ncon*nw, dtype='uint32')
post = np.zeros(Ncon*nw, dtype='uint32')
delay = np.zeros(Ncon*nw, dtype='uint32')
d_w_p = np.zeros(Nneur, dtype=fltSize)

for idx, w_p in enumerate(w_ps):
    pre[idx*Ncon:(idx + 1)*Ncon] = random.randint(idx*N,(idx + 1)*N, Ncon).astype('uint32')
    post[idx*Ncon:(idx + 1)*Ncon] = random.randint(idx*N,(idx + 1)*N, Ncon).astype('uint32')
    delay[idx*Ncon:(idx + 1)*Ncon] = (getDelays(Ncon)/h).astype('uint32')
    d_w_p[idx*N:(idx + 1)*N] = np.zeros(N, dtype=fltSize) + w_p*np.e/tau_psc

weight = np.zeros(Ncon*nw, dtype=fltSize) + w_n*np.e/tau_psc

spike_times = np.zeros((int(SimTime/10) + 2, Nneur), dtype='uint32')
num_spikes_neur = np.zeros(Nneur, dtype='uint32')

Vrec = np.zeros((int((Tsim  + recInt - 1)/recInt), Nneur), dtype=fltSize)

v0, n0, m0, h0 = 32.906693, 0.574676, 0.913177, 0.223994
#v0, n0, m0, h0 = -60.8457, 0.3763, 0.0833, 0.4636
Vm = np.zeros(Nneur, dtype=fltSize) + v0
ns = np.zeros(Nneur, dtype=fltSize) + n0
ms = np.zeros(Nneur, dtype=fltSize) + m0
hs = np.zeros(Nneur, dtype=fltSize) + h0

#phases = random.choice(len(np.load('../Vm_cycle.npy')), Nneur)
#Vm = np.load('../Vm_cycle.npy')[phases]
#ns = np.load('../n_cycle.npy')[phases]
#ms = np.load('../m_cycle.npy')[phases]
#hs = np.load('../h_cycle.npy')[phases]

#Ie = 7.134 + 0.01*random.randn(Nneur).astype(fltSize)
Ie = 5.27 + 0.0*random.randn(Nneur).astype(fltSize)
#Ie[:int(Nneur/2)] = 0.0
#Ie = np.zeros(Nneur, dtype=fltSize) + 7.134
y = np.zeros(Nneur, dtype=fltSize)
Isyn = np.zeros(Nneur, dtype=fltSize)

NnumSp = 1
wInc = 0.0
nums = np.zeros(Nneur, dtype='uint32') + 1
incTimes = np.zeros((NnumSp, Nneur), dtype='uint32')
incSpWeights = np.zeros((NnumSp, Nneur), dtype=fltSize) + wInc*np.e/tau_psc
#%%
phh.setCalcParams(Tsim, Nneur, Ncon, recInt, h)

phh.setIncomSpikes(incTimes, nums, incSpWeights, NnumSp)
phh.setNeurVars(Vm, Vrec, ns, ms, hs)
phh.setCurrents(Ie, y, Isyn, rate, tau_psc, d_w_p, psn_seed)

phh.setSpikeTimes(spike_times, num_spikes_neur, np.shape(spike_times)[0]*Nneur)

phh.setConns(weight, delay,  pre, post)

phh.simulate()
#%%
#pl.figure()
#pl.plot(np.linspace(0, SimTime/1000, int((Tsim + recInt - 1)/recInt)), Vrec[:, 5])
#pl.xlabel('Time, s')
#pl.ylabel('Membrane potential, mV')
#pl.show()
#pl.xlim((0, SimTime/1000))
#%%
#pl.hold(True)
#for idx, w_p in enumerate(xrange(Nneur)):
#    pl.plot(np.linspace(0, SimTime/1000, int((Tsim + recInt - 1)/recInt)), Vrec[:, idx], label=str(idx))
#pl.legend()
#%%
# combine all spike
import numpy.ma as ma
#
spikes = spike_times[:num_spikes_neur[0], 0]
senders = np.array([0]*num_spikes_neur[0])
for i, nsp in zip(xrange(1, Nneur), num_spikes_neur[1:]):
    spikes = np.concatenate((spikes, spike_times[:nsp, i]))
    senders = np.concatenate((senders, [i]*nsp))

(f, ax) = pl.subplots(nw, 1, sharex=True, sharey=True)
for idx, a in enumerate(ax):
    mask = ma.masked_inside(senders, N*idx, N*(idx + 1) - 1)
    a.hist(spikes[mask.mask]*h/1000, bins=int(SimTime/20), histtype='step')
#    a.plot(spikes[mask.mask]*h/1000, senders[mask.mask], '.')
    a.set_title(w_ps[idx])
#pl.xlabel('Time, s')

pl.show()
