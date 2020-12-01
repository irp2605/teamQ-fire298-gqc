import numpy as np
import matplotlib.pyplot as plt
import os
import warnings
import torch
import torch.nn as nn
from model import * #Load custom model
from splitDatasets import *
import argparse
from varname import *

#give 2 1d arrays
def ratioPlotter(inp,out,ifeature,classLabel = ''):
	hIn,binsIn, patchIn = plt.hist(x=inp,bins=60,range =(0,1),alpha=0.5,histtype='step',linewidth=2.5,label='Original '+classLabel)
	hOut,binsOut, patch = plt.hist(x=out,bins=60,range = (0,1),alpha=0.5,histtype='step',linewidth = 2.5,label='Output '+classLabel)
	plt.xlabel('feature '+str(ifeature))
	plt.ylabel('Entries/Bin')
	plt.title('Distribution of '+varname(i))
	plt.legend()


#use gpu if available
with warnings.catch_warnings():
	warnings.simplefilter("ignore")
	device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

infiles = ('../input_ae/trainingTestingDataSig.npy','../input_ae/trainingTestingDataBkg.npy')

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=str, default=infiles, nargs =2, help="path to datasets")
parser.add_argument('--model',type=str,required=True,help='path to saved model')
parser.add_argument('--layers',type=int,required=True,nargs='+',help='type hidden layers nodes corresponding to saved model')
parser.add_argument('--batch',type=int,default=128,help='batch size for testing histogram plot')
parser.add_argument('--fileFlag',type=str,default='',help='fileFlag to concatenate to filetag')

args = parser.parse_args()
infiles = args.input
(savedModel,layers,batch_size,fileFlag) = (args.model,args.layers,args.batch,args.fileFlag)

_,validDataset,testDataset = splitDatasets(infiles)#Load test samples
testLoader = torch.utils.data.DataLoader(arrayData(testDataset),batch_size = testDataset.shape[0],shuffle = False)
validLoader = torch.utils.data.DataLoader(arrayData(validDataset),batch_size = validDataset.shape[0],shuffle = False)

feature_size = testDataset.shape[1]
layers.insert(0,feature_size)

model = AE(node_number = layers).to(device)
model.load_state_dict(torch.load(savedModel+'bestModel.pt'))
model.eval()

criterion = nn.MSELoss(reduction= 'mean')

#if __name__ == "__main__":
testDataSig, testDataBkg = splitDatasets(infiles,separate=True)
testLoaderSig = torch.utils.data.DataLoader(arrayData(testDataSig),batch_size = testDataSig.shape[0],shuffle = False)
testLoaderBkg = torch.utils.data.DataLoader(arrayData(testDataBkg),batch_size = testDataBkg.shape[0],shuffle = False)

#Latent pdf's & input-vs-output pdf's:
with torch.no_grad():
	#MSE on whole validation & test samples:
	dataIter = iter(testLoader)
	inp = dataIter.next()
	output, latentOutput = model(inp.float())
	print('Test sample MSE:',criterion(output,inp).item())
	
	dataIter = iter(validLoader)
	inp = dataIter.next()
	output, latentOutput = model(inp.float())
	print('Validation sample MSE:',criterion(output,inp).item())
	
	#Latent pdf's:
	dataIter = iter(testLoaderSig)
	inpSig = dataIter.next()
	outputSig, latentOutputSig = model(inpSig.float())
	dataIter = iter(testLoaderBkg)
	inpBkg = dataIter.next()
	outputBkg, latentOutputBkg = model(inpBkg.float())
	latentOutputSig,latentOutputBkg = latentOutputSig.numpy(), latentOutputBkg.numpy()
	
	for i in range(latentOutputSig.shape[1]):
		hSig,_,_ = plt.hist(x=latentOutputSig[:,i],density=1,bins=60,alpha=0.6,histtype='step',linewidth=2.5,label='Sig')
		hBkg,_,_ = plt.hist(x=latentOutputBkg[:,i],density=1,bins=60,alpha=0.6,histtype='step',linewidth=2.5,label='Bkg')
		plt.legend()
		plt.xlabel(f'Latent feature {i}')
		plt.savefig(savedModel+'latentPlot'+str(i)+'.png')
		plt.clf()	

	#Input VS Output:
	for i in range(inpSig.numpy().shape[1]):
		ratioPlotter(inpSig.numpy()[:,i],outputSig.numpy()[:,i],i,classLabel='Signal')#Plot Signal distributions
		ratioPlotter(inpBkg.numpy()[:,i],outputBkg.numpy()[:,i],i,classLabel='Background')#Plot Background distributions
		
		plt.savefig(savedModel+'ratioPlot'+str(i)+'.png')
		plt.clf()
	
	samples = ['Sig','Bkg']
	colors = ['b','r']
	labels = ['Test on Sig.', 'Test on Bkg.']
	##MSE loss in test samples.
	for j,isample in enumerate(samples):
		test_loader = torch.utils.data.DataLoader(testDataset,batch_size = batch_size,shuffle = False)
		meanLossBatch = []
		for i,batch_features in enumerate(test_loader):
			batch_features = batch_features.view(-1, feature_size).to(device)
			output = model(batch_features)
			loss = criterion(output,batch_features)
			meanLossBatch.append(loss.item())
		
		plt.hist(meanLossBatch,bins=20,density = 0,color=colors[j],alpha=0.5, ec='black',label=labels[j])
		plt.ylabel('Entries/Bin')
		plt.xlabel('MSE per Batch')
		plt.title('MSE per batch, Ntest={}.'.format(len(testDataset)))
	plt.legend()
	plt.savefig(savedModel+'/testloss'+filetag)
