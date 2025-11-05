import HelperFunctions as hp

def FreeExpansion(stent_location):
    model = 'CYL-STENT'
    mdb.models.changeKey(fromName = 'Model-1', toName=model)
    MatCoCr(model)
    Balloon(model)
    stent_importSTEP_mesh(model, 'STENT', stent_location)
    assembly_cyl_stent(model)
    mdb.Job(name='FreeExp', model=model, description='', type=ANALYSIS, 
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, numDomains=1, 
        activateLoadBalancing=False, numThreadsPerMpiProcess=1, 
        multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
    mdb.jobs['FreeExp'].writeInput(consistencyChecking=OFF)
    mdb.close()
    mdb.ModelFromInputFile(name='FreeExp', inputFileName='E:/Andrea/FreeExp.inp')
    del mdb.models['Model-1']
    free_exp_addons('FreeExp')
    mdb.Job(name='FreeExpFull', model=model, description='', type=ANALYSIS, 
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, numDomains=1, 
        activateLoadBalancing=False, numThreadsPerMpiProcess=1, 
        multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
    mdb.jobs['FreeExpFull'].writeInput(consistencyChecking=OFF)