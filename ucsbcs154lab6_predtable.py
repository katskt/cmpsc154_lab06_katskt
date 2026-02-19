# ucsbcs154lab6
# All Rights Reserved
# Copyright (c) 2023 University of California Santa Barbara
# Distribution Prohibited
import pyrtl

pyrtl.core.set_debug_mode()

##### INITIALIZATION #####

# Inputs
fetch_pc = pyrtl.Input(bitwidth=32, name='fetch_pc') # current pc in fetch

update_prediction = pyrtl.Input(bitwidth=1, name='update_prediction') # whether to update prediction
update_branch_pc = pyrtl.Input(bitwidth=32, name='update_branch_pc') # previous pc (in decode/execute)
update_branch_taken = pyrtl.Input(bitwidth=1, name='update_branch_taken') # whether branch is taken (in decode/execute)

# Outputs
pred_taken = pyrtl.Output(bitwidth=1, name='pred_taken')
pred_state = pyrtl.MemBlock(bitwidth= 2, addrwidth=3, name = 'pred_state', max_read_ports = 50, max_write_ports = 3)  # bitwidth = bitwidth of each element in memory. 2 bits for 00, 01, 10, 11. # addrwidth = the number of bits used to address an element in memory. 
# pred_state_register = pyrtl.Register(bitwidth=2, name = 'pred_state_register') # remembers the current state so that it can be updated.
# Write your BHT branch predictor here
# addressing into BHT using PC
pred_state_index = pyrtl.WireVector(bitwidth = 3, name = 'pred_state_index')
update_branch_pc_index = pyrtl.WireVector(bitwidth = 3, name = 'update_branch_pc_index')

####### LOGIC #######

pred_state_index <<= fetch_pc[2:5] # CURRENT ADDR INDEX  0 is LSB, start at 2. 2, 3, 4. 5 EXCLUSIVE. 

update_branch_pc_index <<= update_branch_pc[2:5] # PREV ADDR INDEX

temp = pyrtl.WireVector(bitwidth = 2, name = "temp")
# update old checked with the correct value


## FOR CURRENT ADDR, GIVES THE PREDICTION (1BIT)
with pyrtl.conditional_assignment: 
    with pred_state[pred_state_index] >= 0b10:
        pred_taken |= pyrtl.Const(val=1)
    with pyrtl.otherwise:
        pred_taken |= pyrtl.Const(val=0)

# MANAGES STATE

with pyrtl.conditional_assignment:
    with update_prediction: # if this is a branch instr
        with update_branch_taken: # if this was a branch taken 
            with pred_state[update_branch_pc_index] != 0b11:
                temp |= pred_state[update_branch_pc_index] + pyrtl.Const(1)
            with pyrtl.otherwise:
                temp |= pred_state[update_branch_pc_index]
            # do something
        with pyrtl.otherwise: # if this was a NOT branch taken, ie 
            with pred_state[update_branch_pc_index] != 0b00:
                temp |= pred_state[update_branch_pc_index] - pyrtl.Const(1)
            with pyrtl.otherwise:
                temp |= pred_state[update_branch_pc_index]
    with pyrtl.otherwise:
        temp |= pred_state[update_branch_pc_index] # assign to previous, which is in rf. 

pred_state[update_branch_pc_index] <<= pred_state.EnabledWrite(temp, enable=(1)) 
""" 
Use for debubggyy 
bit000 = pyrtl.WireVector(bitwidth = 2, name = "bit0")
bit001 = pyrtl.WireVector(bitwidth = 2, name = "bit1")
bit010 = pyrtl.WireVector(bitwidth = 2, name = "bit2")
bit011 = pyrtl.WireVector(bitwidth = 2, name = "bit3")
bit100 = pyrtl.WireVector(bitwidth = 2, name = "bit4")
bit101 = pyrtl.WireVector(bitwidth = 2, name = "bit5")
bit110 = pyrtl.WireVector(bitwidth = 2, name = "bit6")
bit111 = pyrtl.WireVector(bitwidth = 2, name = "bit7")

bit000 <<= pred_state[0]
bit001 <<= pred_state[1]
bit010 <<= pred_state[2]
bit011 <<= pred_state[3]
bit100 <<= pred_state[4]
bit101 <<= pred_state[5]
bit110 <<= pred_state[6]
bit111 <<= pred_state[7] 
 """
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
    f = open("tests/bht2_code.txt", "r")  # Edit this line to change the trace file you read from
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

    print('pred_state', sim.inspect_mem(pred_state))
