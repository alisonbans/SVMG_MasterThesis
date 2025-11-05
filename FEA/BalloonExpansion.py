def BalloonExpansion(stent_location = 'D:/Alison/stent_NUS19_CW0.1000_SW0.0600_ST0.0600_CR0.4600.STEP'):
model = 'BALLOON-STENT-ARTERY'
job_name = 'BalloonArteryCriExp'
mdb.models.changeKey(fromName = 'Model-1', toName=model)
MatCoCr(model)
Balloon_Accuforce(model)
expanded_stent(model)
ArteryMaterial(model)
artery(model)
cylinder_cri(model)
assembly_ballonexp(model)
mdb.Job(name='BalloonExp', model=model, description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, numDomains=1, 
    activateLoadBalancing=False, numThreadsPerMpiProcess=1, 
    multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
mdb.jobs['BalloonExp'].writeInput(consistencyChecking=OFF)
mdb.close()
mdb.ModelFromInputFile(name='BalloonExp', inputFileName='E:/Andrea/BalloonExp.inp')
del mdb.models['Model-1']
balloon_exp_addons('BalloonExp', deltaT = 1e-05)
mdb.Job(name=job_name, model='BalloonExp', description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, numDomains=1, 
    activateLoadBalancing=False, numThreadsPerMpiProcess=1, 
    multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
mdb.jobs[job_name].writeInput(consistencyChecking=OFF)
