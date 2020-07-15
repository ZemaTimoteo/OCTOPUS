# Copyright of the Board of Trustees of Columbia University in the City of New York
'''
Numerical Simulation Experiments with spiral trajectory
Author: Marina Manso Jimeno
Last updated: 07/15/2020
'''
import numpy as np
import math
import cv2
import matplotlib.pyplot as plt

import OCTOPUS.ORC as ORC
import OCTOPUS.utils.fieldmap.fieldmap_gen as fieldmap_gen
from OCTOPUS.utils.plot_results import plot_correction_results

##
# Original image: Shep-Logan Phantom
##
ph = np.load('../Recon/test_data/slph_im.npy').astype(complex) # Shep-Logan Phantom
ph = (ph - np.min(ph)) / (np.max(ph)-np.min(ph)) # Normalization
N = ph.shape[0]
plt.imshow(np.abs(ph), cmap='gray')
plt.title('Original phantom')
plt.axis('off')
plt.colorbar()
plt.show()

##
# Spiral k-space trajectory
##
dt = 10e-6
ktraj = np.load('../Recon/test_data/ktraj_noncart.npy') # k-space trajectory
#TODO: Remove the scaling
'''ktraj_sc = math.pi / abs(np.max(ktraj))
ktraj = ktraj * ktraj_sc # pyNUFFT scaling [-pi, pi]'''
plt.plot(ktraj.real,ktraj.imag)
plt.title('Spiral trajectory')
plt.show()

#ktraj_dcf = np.load('test_data/ktraj_noncart_dcf.npy').flatten() # density compensation factor
t_ro = ktraj.shape[0] * dt
T = (np.arange(ktraj.shape[0]) * dt).reshape(ktraj.shape[0],1)

seq_params = {'N': ph.shape[0], 'Npoints': ktraj.shape[0], 'Nshots': ktraj.shape[1], 't_readout': t_ro, 't_vector': T}#, 'dcf': ktraj_dcf}
##
# Simulated field map
##
fmax_v = [250, 500, 750] # Hz

i = 0
or_corrupted = np.zeros((N, N, len(fmax_v)), dtype='complex')
or_corrected_CPR = np.zeros((N, N, len(fmax_v)), dtype='complex')
or_corrected_fsCPR = np.zeros((N, N, len(fmax_v)), dtype='complex')
or_corrected_MFI = np.zeros((N, N, len(fmax_v)), dtype='complex')
for fmax  in fmax_v:

    field_map = fieldmap_gen.realistic(np.abs(ph), fmax)
    ### For reproducibility
    '''dst = np.zeros((N, N))
    field_map = cv2.normalize(np.load('M2.npy'), dst, -fmax, fmax, cv2.NORM_MINMAX)
    field_map = field_map * np.load('mask.npy')
    field_map = fieldmap_gen.fieldmap_bin(field_map,5)'''
    ###
    plt.imshow(field_map, cmap='gray')
    plt.title('Field Map +/-' + str(fmax) + ' Hz')
    plt.colorbar()
    plt.axis('off')
    plt.show()

##
# Corrupted images
##
    or_corrupted[:,:,i] = ORC.add_or_CPR(ph, ktraj, field_map, 1, seq_params)
    plt.imshow(np.abs(or_corrupted[:,:,i]),cmap='gray')
    plt.colorbar()
    plt.axis('off')
    plt.show()

###
# Corrected images
###
    or_corrected_CPR[:, :, i] = ORC.CPR(or_corrupted[:, :, i], 'im', ktraj, field_map, 1, seq_params)
    print('CPR done')
    or_corrected_fsCPR[:, :, i] = ORC.fs_CPR(or_corrupted[:, :, i], 'im', ktraj, field_map, 2, 1, seq_params)
    print('fs-CPR done')
    or_corrected_MFI[:,:,i] = ORC.MFI(or_corrupted[:,:,i], 'im', ktraj, field_map, 2, 1, seq_params)
    print('MFI done')
    i += 1

##
# Plot
##

# Metrics
im_stack = np.stack((np.squeeze(or_corrupted), np.squeeze(or_corrected_CPR), np.squeeze(or_corrected_fsCPR), np.squeeze(or_corrected_MFI)))
np.save('im_stack.npy',im_stack)
cols = ('Corrupted Image','CPR Correction', 'fs-CPR Correction', 'MFI Correction')
row_names = ('-/+ 250 Hz', '-/+ 500 Hz', '-/+ 750 Hz')
plot_correction_results(im_stack, cols, row_names)


