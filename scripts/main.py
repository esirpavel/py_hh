# coding: utf-8
'''
Created on 29 июня 2016 г.

@author: Pavel Esir
'''
fltSize = 'float32'
from py_hh import *
import numpy as np
import matplotlib.pylab as pl
np.random.seed(0)
psn_seed = 1

Ntrans = 280 # length of transient process in periods, integer
T = 20.28
SimTime = (Ntrans+0.5)*T
#SimTime = 200.
h = 0.02
Tsim = int(SimTime/h)
recInt = 5

tau_psc = 0.2  # ms
w_p = 2.0      # Poisson noise weith, pA
w_n = 5.0      # connection weight, pA
#w_n = .0      # connection weight, pA

#rate = 185.0     # Poisson noise rate, Hz (shouldn't  be 0)
#Nneur = 100
#Ncon = int(Nneur*Nneur*0.2)
#Nneur = int(T/h)
#Ncon = 1
#pre = np.random.randint(0, Nneur, Ncon).astype('uint32')
#post = np.random.randint(0, Nneur, Ncon).astype('uint32')
#delay = np.array([4.0/h]*Ncon).astype('uint32') # delay arrays in time frames
#delay = np.random.lognormal(1.8, 1/6.0, Ncon).astype('uint32') # delay arrays in time frames

Nneur = 2
Ncon = 2
pre = np.array([0, 1], dtype='uint32')
post = np.array([1, 0], dtype='uint32')
delay = (np.ones(Ncon)*4.5/h).astype('uint32') # delay arrays in time frames
#delay = (np.ones(Ncon)*0.0/h).astype('uint32') # delay arrays in time frames
rate = np.zeros(Nneur, dtype=fltSize) + 200     # Poisson noise rate, Hz (shouldn't  be 0)

# int(SimTime/10) тут 10 это период в мс максимального ожидаемого интервала между спайками
spike_times = np.zeros((int(SimTime/10) + 2, Nneur), dtype='uint32')
num_spikes_neur = np.zeros(Nneur, dtype='uint32')

weight = np.zeros(Ncon, dtype=fltSize) + w_n*np.e/tau_psc

setCalcParams(Tsim, np.iinfo(np.int32).max, Nneur, Ncon, recInt, h)

Vrec = np.zeros((int((Tsim  + recInt - 1)/recInt), Nneur), dtype=fltSize)

v0, n0, m0, h0 = 32.906693, 0.574676, 0.913177, 0.223994
Vm = np.zeros(Nneur, dtype=fltSize) + v0
ns = np.zeros(Nneur, dtype=fltSize) + n0
ms = np.zeros(Nneur, dtype=fltSize) + m0
hs = np.zeros(Nneur, dtype=fltSize) + h0
dPhase = int(10.0/0.02)
Vm[1] = np.load('../Vm_cycle.npy')[dPhase]
ns[1] = np.load('../n_cycle.npy')[dPhase]
ms[1] = np.load('../m_cycle.npy')[dPhase]
hs[1] = np.load('../h_cycle.npy')[dPhase]

NnumSp = 1
wInc = 0.0
nums = np.zeros(Nneur, dtype='uint32')
incTimes = np.zeros((NnumSp, Nneur), dtype='uint32')
incSpWeights = np.zeros((NnumSp, Nneur), dtype=fltSize) + wInc*np.e/tau_psc
dts = np.arange(0, Nneur, dtype='uint32')
for i in xrange(NnumSp):
    incTimes[i, :] = (i + 1)*dts
incSpWeights[0, :] = wInc*np.e/tau_psc
nums[:] = 1
#inc_spikes = {1: np.array([40, 50])}
#for k, v in inc_spikes.iteritems():
#    incTimes[0:len(v), k] = np.array(v/h, dtype='uint32')
#    incSpWeights[0:len(v), k] = wInc
#    nums[k] = len(v)
setIncomSpikes(incTimes, nums, incSpWeights, NnumSp)
#%%
#Ie = np.zeros(Nneur) + 5.27

Ie = np.zeros(Nneur, dtype=fltSize)
Ie[:] = 5.27

y = np.zeros(Nneur, dtype=fltSize)
Isyn = np.zeros(Nneur, dtype=fltSize)
d_w_p = np.zeros(Nneur, dtype=fltSize) + w_p*np.e/tau_psc

setNeurVars(Vm, Vrec, ns, ms, hs)
setCurrents(Ie, y, Isyn, rate, tau_psc, d_w_p, psn_seed)

setSpikeTimes(spike_times, num_spikes_neur, np.shape(spike_times)[0]*Nneur)

setConns(weight, delay,  pre, post)
#%%
simulate()
if num_spikes_neur[0] > int(Ntrans/2)and num_spikes_neur[1] > int(Ntrans/2):
    print(abs(spike_times[num_spikes_neur[0] - 1, 0]*h - spike_times[num_spikes_neur[1] - 1, 1]*h))
#%%
pl.figure()
pl.plot(np.linspace(0, SimTime, int((Tsim + recInt - 1)/recInt)), Vrec[:, :10])
pl.xlabel('time (ms)')
pl.ylabel('Membrane potential (mV)')
pl.show()
pl.xlim((0, SimTime))
#np.save('h_cycle.npy', Vrec[4054:5069, 0])
#%%
#pl.figure()
## combine all spike
#spikes = spike_times[:num_spikes_neur[0], 0]
#senders = np.array([0]*num_spikes_neur[0])
#for i, nsp in zip(xrange(1, Nneur), num_spikes_neur[1:]):
#    spikes = np.concatenate((spikes, spike_times[:nsp, i]))
#    senders = np.concatenate((senders, [i]*nsp))
#
#pl.plot(spikes*h, senders, '.')
####pl.xlim((0, 200))
#pl.show()

#pl.hist(spikes*h, bins=int(SimTime/20), histtype='step')
#pl.xlabel('time, ms')
#pl.ylabel('Membrane potential, mV')
#pl.show()
#
#%%
#pl.figure(1)
#msc = np.zeros(np.shape(spike_times), dtype='bool')
#lastSpikeTime = np.zeros(Nneur)
#for i, n in enumerate(num_spikes_neur):
#    if n != 0:
#        lastSpikeTime[i] = spike_times[n - 1, i]
#        if n < Ntrans:
#            lastSpikeTime[i] = np.nan
#    else:
#        lastSpikeTime[i] = np.nan
#
#pl.plot(dts*h, np.ma.array((Ntrans*T + h*dts) - h*lastSpikeTime, mask=(lastSpikeTime != lastSpikeTime)), '-')
#pl.plot(arange(0, T, 0.01), arange(0, T, 0.01))
#pl.ylim((0, T))
#pl.xlim((0, T))
#pl.show()
