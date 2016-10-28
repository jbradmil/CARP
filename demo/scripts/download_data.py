import MySQLdb as mdb
from bg_est import BGEst
from math import sqrt

def download_data(model, mMom, mLSP, username):

    ## Step 1: read the data in from SQL database   

    ## now connect to the SQL database
    con = mdb.connect(host='localhost', user=username, db='ra2')
    with con:
        cur = con.cursor()
        ## get the observed data
        data_obs = []
        cur.execute("SELECT * FROM data_obs")
        for i in range(cur.rowcount):
            row = cur.fetchone()
            data_obs.append(int(row[1]))
        ## get znn background estimation
        znn = BGEst()
        cur.execute("SELECT * FROM znn")
        for i in range(cur.rowcount):
            row = cur.fetchone()
            znn.AddBin(float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]))
        ## get qcd background estimation
        qcd = BGEst()
        cur.execute("SELECT * FROM qcd")
        for i in range(cur.rowcount):
            row = cur.fetchone()
            qcd.AddBin(float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]))
        ## get lost lepton and hadronic tau background estimations -- combine them into one (wtop)
        lostlep = BGEst()
        cur.execute("SELECT * FROM lostlep")
        for i in range(cur.rowcount):
            row = cur.fetchone()
            lostlep.AddBin(float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]))
        hadtau = BGEst()
        cur.execute("SELECT * FROM hadtau")
        for i in range(cur.rowcount):
            row = cur.fetchone()
            hadtau.AddBin(float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]))
        # combine into one wtop BG, correlating stat err but not syst err
        wtop = BGEst([a+b for a,b in zip(lostlep.CV,hadtau.CV)],\
                     [a+b for a,b in zip(lostlep.statUp,hadtau.statUp)],\
                     [a+b for a,b in zip(lostlep.statDown,hadtau.statDown)],\
                     [sqrt(a**2+b**2) for a,b in zip(lostlep.systUp,hadtau.systUp)],\
                     [sqrt(a**2+b**2) for a,b in zip(lostlep.systDown,hadtau.systDown)])
        # finally, get the expected signal yields
        # identify the table and column
        signal_table = model
        signal_column = "_".join([signal_table, str(mMom), str(mLSP)])
        signal = []
        cur.execute("SELECT %s FROM %s" % (signal_column, signal_table))
        for i in range(cur.rowcount):
            row = cur.fetchone()
            signal.append(float(row[0]))

    return data_obs, wtop, znn, qcd, signal
