# ucsbcs154lab6
# All Rights Reserved
# Copyright (c) 2023 University of California Santa Barbara
# Distribution Prohibited

import pyrtl

pyrtl.core.set_debug_mode()

# Inputs
fetch_pc = pyrtl.Input(bitwidth=32, name='fetch_pc') # current pc in fetch

update_prediction = pyrtl.Input(bitwidth=1, name='update_prediction') # whether to update prediction
update_branch_pc = pyrtl.Input(bitwidth=32, name='update_branch_pc') # previous pc (in decode/execute)
update_branch_taken = pyrtl.Input(bitwidth=1, name='update_branch_taken') # whether branch is taken (in decode/execute)

# Outputs
pred_taken = pyrtl.Output(bitwidth=1, name='pred_taken')
pred_state = pyrtl.Register(bitwidth = 2, name = 'pred_state')


#helper

temp = pyrtl.WireVector(bitwidth = 2, name = "temp")

####### LOGIC #######

## if i am in state 
## if state is in the 2 states, then output yes update. else do no dont update.
with pyrtl.conditional_assignment: 
    with update_prediction:
        with temp >= 0b10:
            pred_taken |= pyrtl.Const(val=1)
        with pyrtl.otherwise:
            pred_taken |= pyrtl.Const(val=0)
    with pyrtl.otherwise:
        with temp >= 0b10:
            pred_taken |= pyrtl.Const(val=1)
        with pyrtl.otherwise:
            pred_taken |= pyrtl.Const(val=0)

# this manages the 2bit state
with pyrtl.conditional_assignment:
    with update_prediction: # if this is a branch instr
        with update_branch_taken: # if this was a branch taken 
            with pred_state != 0b11:
                temp |= pred_state + pyrtl.Const(1)
            with pyrtl.otherwise:
                temp |= pred_state
            # do something
        with pyrtl.otherwise: # if this was a NOT branch taken, ie 
            with pred_state != 0b00:
                temp |= pred_state - pyrtl.Const(1)
            with pyrtl.otherwise:
                temp |= pred_state
    with pyrtl.otherwise:
        temp |= pred_state
        
pred_state.next <<= temp
# new pred is 0 and update is 0 do nothing. if its 1 and udate is 1 do nothing. else add 1 or sub 1 or whatever. 



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
    f = open("tests/2bit2_code.txt", "r")  # Edit this line to change the trace file you read from
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

    sim_trace.render_trace()
    print("Accuracy = ", correct/count)
