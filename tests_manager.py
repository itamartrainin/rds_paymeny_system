# Liveness:
# run X steps
# call close() to simulatior
    # 0 all action rates - get,pay,transform
# Run steps until msg_queue is empty
# Show all clients are not during_action

# Can run another where a client has omission, and then it can be faulty - not a must


# Safety
# do log 
# report log

# when agent does action 
    # write to do_log and to report_log
# when action finishes - when upon triggers
    # write to report_log + answer (get)

# run simulation with random actions + writing to log
    # run x steps
    # call close
    # run until finish
# run simulation without random actions, but with reading the log
    # run x steps
    # call close
    # run until finish
# Compare results
    # gets receives always the same answer - go over the report_log
    # pay works good - compare the collective active DB (only servers)


# Get
# pay 1
# pay 2