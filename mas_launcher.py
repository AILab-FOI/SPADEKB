from LauncherAgent import LauncherAgent

import spade

import time

# import logging

if __name__ == "__main__":

    print("SPADE version: ", spade.__version__)

    # logging.basicConfig(level=logging.INFO)

    xmpp_server = "gtirouter.dsic.upv.es"

    jid_launch = "launcher" + "@" + xmpp_server
    passwd_launch = "test"
    ag_launcher = LauncherAgent(jid_launch, passwd_launch, use_container=False)
    ag_launcher.web.port = 33000
    ag_launcher.port = ag_launcher.web.port + 3000
    ag_launcher.start(auto_register=True)

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            ag_launcher.stop()
            break

    '''
    for jid, agent in ag_launcher.mas_dict.items():
        with open('{}_trace.txt'.format(jid), 'w') as f:
            for event in agent.traces.filter(category='Barrier'):
                f.write('[{}] {}\n'.format(event[0], event[1].body))
    '''

    print("Finished")
