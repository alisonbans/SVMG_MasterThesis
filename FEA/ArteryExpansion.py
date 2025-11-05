import HelperFunctions as hp 

def ArteryExpansion(stent_location = 'D:/Alison/stent_NUS19_CW0.1000_SW0.0600_ST0.0600_CR0.4600.STEP'):
    model = 'CYL-STENT-ARTERY'
    mdb.models.changeKey(fromName = 'Model-1', toName=model)
    MatCoCr(model)
    Balloon(model)
    expanded_stent(model)
    ArteryMaterial(model)
    artery(model)
    assembly_cyl_stent(model)
    assembly_artery(model)
    cylinder_cri(model)
    assembly_cyl_crimp(model)
    mdb.Job(name='ArteryExp', model=model, description='', type=ANALYSIS, 
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, numDomains=1, 
        activateLoadBalancing=False, numThreadsPerMpiProcess=1, 
        multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
    mdb.jobs['ArteryExp'].writeInput(consistencyChecking=OFF)
    mdb.close()
    mdb.ModelFromInputFile(name='ArteryExp', inputFileName='E:/Andrea/ArteryExp.inp')
    del mdb.models['Model-1']
    free_exp_addons('ArteryExp')
    artery_exp_addons('ArteryExp')
    mdb.Job(name='ArteryCriExp', model='ArteryExp', description='', type=ANALYSIS, 
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, numDomains=1, 
        activateLoadBalancing=False, numThreadsPerMpiProcess=1, 
        multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
    mdb.jobs['ArteryCriExp'].writeInput(consistencyChecking=OFF)