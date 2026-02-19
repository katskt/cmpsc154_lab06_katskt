# ucsbcs154lab6
# All Rights Reserved
# Copyright (c) 2023 University of California Santa Barbara
# Distribution Prohibited

import pyrtl

pyrtl.core.set_debug_mode()

####### Inputs #######

# current pc in FETCH STAGE
fetch_pc = pyrtl.Input(bitwidth=32, name='fetch_pc') 

update_prediction = pyrtl.Input(bitwidth=1, name='update_prediction') 

# previous pc (in DECODE/EXECUTE STAGE)
update_branch_pc = pyrtl.Input(bitwidth=32, name='update_branch_pc') 

update_branch_taken = pyrtl.Input(bitwidth=1, name='update_branch_taken') 

####### Outputs #######
pred_taken = pyrtl.Output(bitwidth=1, name='pred_taken')

pred_state = pyrtl.Register(bitwidth=1, name="pred_state")

new_pred_state = pyrtl.WireVector(bitwidth=1, name="new_pred_state")

####### LOGIC #######

pred_taken <<= pyrtl.select(update_prediction, new_pred_state, pred_state)

pred_state.next <<= new_pred_state

with pyrtl.conditional_assignment:
    with update_prediction:
        new_pred_state |= update_branch_taken
    with pyrtl.otherwise:
        new_pred_state |= pred_state


# Testing
if __name__ == "__main__":
    sim_trace = pyrtl.SimulationTrace()
    sim = pyrtl.Simulation(tracer=sim_trace)
    pcPrevious = 0
    branchTakenPrevious = 0
    isBranchPrevious = 0
    predictionPrevious = 0
    count = 0
    correct = 0
    f = open("demo_trace.txt", "r")  # Edit this line to change the trace file you read from
    for iteration,line in enumerate(f): # Read through each line in the file
        pcCurrent = int(line[0:line.find(':')],0) # parse out current pc
        branchTakenCurrent = int(line[12]) # parse out branch taken
        isBranchCurrent = int(line[16]) # parse if the current instr is a branch

        sim.step({ # Feed in input values
            'fetch_pc' : pcCurrent,
            'update_branch_pc' : pcPrevious,
            'update_prediction': isBranchPrevious,
            'update_branch_taken' : branchTakenPrevious
        })

        predictionCurrent = sim_trace.trace['pred_taken'][-1] # get the value of your prediction

        if isBranchPrevious: # check if previous instr was a branch
            if predictionPrevious == branchTakenPrevious: # if prediction was correct
                correct += 1
            count += 1


        # Update for next cycle
        pcPrevious = pcCurrent
        branchTakenPrevious = branchTakenCurrent
        isBranchPrevious = isBranchCurrent
        predictionPrevious = predictionCurrent

    # one final check
    if isBranchPrevious:
        if predictionPrevious == branchTakenPrevious:
            correct += 1 # Correct prediction
        count += 1

    print("Accuracy = ", correct/count)
    sim_trace.render_trace()
